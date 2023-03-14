/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023 by Christoph Schueler <cpu12.gems.googlemail.com>

    All Rights Reserved

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

    s. FLOSS-EXCEPTION.txt
*/

#if !defined(__PREPROCESSOR_HPP)
#define __PREPROCESSOR_HPP

#include <algorithm>
#include <filesystem>
#include <iostream>
#include <iterator>
#include <fstream>
#include <map>
#include <optional>
#include <regex>
#include <tuple>
#include <vector>

#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>

namespace fs = std::filesystem;

#include "extensions/ifdata.hpp"
#include "extensions/utils.hpp"
#include "extensions/tempfile.hpp"
#include "extensions/line_map.hpp"
#include "extensions/regex.hpp"

class Preprocessor {
public:

    Preprocessor() : tmp_a2l_pre("A2L_pre.tmp"), tmp_a2l("A2L.tmp"), tmp_aml("AML.tmp"), tmp_ifdata("IFDATA.tmp", true) {
        get_include_paths_from_env();
    }

    ~Preprocessor() {

    }

    void process(const std::string& filename) {
        _process_file(filename);
        line_map.finalize();
        IfDataReader ifdata_reader = _process_aml();
    }

    LineMap line_map{};

protected:
    void _process_file(const std::string& filename) {
        std::uint64_t start_line_number = absolute_line_number + 1;
        fs::path path{ filename };
        auto abs_pth = fs::absolute(path);
        std::ifstream file(abs_pth);

        if (file.is_open()) {
            std::string line;
            std::uint64_t line_num = 0;
            bool multi_line = false;
            bool use_c_match = false;
            bool use_cpp_match = false;
            bool cpp_match = false;
            bool c_match = false;
            bool match = false;
            std::vector<std::string> result;
            std::string rl;

            while (!file.eof()) {
                line_num++;
                absolute_line_number++;
                std::getline(file, line);
                if (file.eof() || !file) {
                    break;
                }
                rstrip(line);
                if (multi_line) {
                    match = re_multiline_end(line);
                    if (match) {
                        multi_line = false;
                        rl = re_multiline_end.str(1);
                        tmp_a2l_pre() << rl << std::endl;
                        continue;
                    }
                    else {
                        rl = "\n";
                        tmp_a2l_pre() << std::endl;
                        continue;
                    }
                }
                cpp_match = re_cpp_comment(line);
                c_match = re_multiline_start(line);
                use_c_match = use_cpp_match = false;
                if (cpp_match && c_match) {
                    if (re_cpp_comment.start(0) < re_multiline_start.start(0)) {
                        use_cpp_match = true;
                    }
                    else {
                        use_c_match = true;
                    }
                }
                else if (c_match) {
                    use_c_match = true;
                }
                else if (cpp_match) {
                    use_cpp_match = true;
                }
                if (use_cpp_match) {
                    rl = re_cpp_comment.prefix();
                }
                else if (use_c_match) {
                    match = re_multiline_end(line);
                    if (match) {
                        multi_line = false;
                        blank_out(line, re_multiline_start.start(0), re_multiline_end.start(1));
                        rl = line;
                    }
                    else {
                        multi_line = true;
                        blank_out(line, re_multiline_start.start(0), -1);
                        rl = line;
                    }
                }
                else {
                    rl = line;
                }
                match = re_include(rl);
                if (match) {
                    line_num--;
                    absolute_line_number--;
                    std::string include_file_name = re_include.str(1);
                    auto where = locate_file(include_file_name, abs_pth.parent_path().string());
                    if (where.has_value()) {
                        update_line_map(abs_pth, start_line_number);
                        _process_file(where.value().string());
                        start_line_number = absolute_line_number + 1;
                    }
                    else {
                        throw std::runtime_error("Can't find include file: '" + include_file_name + "'");
                    }
                }
                else {
                    escape_string(rl);
                    tmp_a2l_pre() << rl << std::endl;
                }
            }
            update_line_map(abs_pth, start_line_number);
            file.close();
        }
        else {
            throw std::runtime_error("Could not open file: '" + abs_pth.string() + "'");
        }
    }

    IfDataReader _process_aml() {
        bool in_aml = false;
        bool in_if_data = false;
        std::uint64_t line_num = 0;
        std::tuple<std::size_t, std::size_t> ifdata_start_line_num, ifdata_end_line_num;
        IfDataBuilder ifdata_builder{ tmp_ifdata.handle() };

        const auto cut_out_ifdata = [&ifdata_builder, &in_if_data, &line_num,
            &ifdata_start_line_num, &ifdata_end_line_num, this](std::string& line) -> void {
            bool match{ false };
            bool single_line{ false };

            //while (true) {
            match = re_if_data_start(line);
            if (match) {
                in_if_data = true;
                auto [start, end] = re_if_data_start.span(0);
                auto s0 = re_if_data_start.str(1);
                auto s1 = re_if_data_start.str(2);
                auto section = re_if_data_start.str(3);
                auto tail = re_if_data_start.str(4);
                auto if_data_start = std::tuple<std::size_t, std::size_t>(line_num, start);
                auto ifdata_head = re_if_data_start.prefix() + "/begin" + s0 + "IF_DATA" + s1 + section;
                ifdata_start_line_num = { line_num, start };
                single_line = false;
                match = re_if_data_end(tail);
                if (match) {
                    //auto [xstart, xend] = re_if_data_end.span(0);
                    auto xsection = re_if_data_end.str(1);
                    auto xs0 = re_if_data_end.str(2);
                    auto xtail = re_if_data_end.str(3);
                    single_line = true;
                    in_if_data = false;
                    auto offset = std::size(ifdata_head) + std::size(xsection) + 4 + 7 + 1;

                    ifdata_end_line_num = { line_num, offset };

                    auto ifdata_end = "/end" + xs0 + "IF_DATA";
                    std::string filler(std::size(line) - (std::size(ifdata_head) + std::size(ifdata_end) + std::size(xtail)), ' ');
                    line = ifdata_head + filler + ifdata_end;
                    auto xxy = xsection + "/end" + xs0 + "IF_DATA";
                }
                else {
                    auto complete_match = re_if_data_start.str(0);
                    ifdata_builder.add_section(complete_match + '\n');
                    line = ifdata_head;
                }
                if (!single_line) {
                    //break;
                }
            }
            else {
                //break;
            }

            //}
        };

        std::ifstream file("A2L_pre.tmp");
        if (file.is_open()) {
            std::string line;
            bool match = false;
            std::string rl;

            while (!file.eof()) {
                line_num++;
                std::getline(file, line);
                if (file.eof() || !file) {
                    break;
                }
                if (!in_aml) {
                    match = re_aml_start(line);
                    if (match) {
                        in_aml = true;
                        tmp_aml() << "/begin A2ML" << std::endl;
                        tmp_a2l() << "/begin A2ML" << std::endl;
                    }
                    else {
                        if (!in_if_data) {
                            cut_out_ifdata(line);
                            tmp_a2l() << line << std::endl;
                        }
                        else {
                            match = re_if_data_end(line);
                            if (match) {
                                auto [start, end] = re_if_data_end.span(0);
                                auto xsection = re_if_data_end.str(1);
                                auto xs0 = re_if_data_end.str(2);
                                auto xtail = re_if_data_end.str(3);
                                in_if_data = false;
                                ifdata_end_line_num = { line_num, end - std::size(xtail) };
                                std::string xfiller(std::size(xsection), ' ');

                                ifdata_builder.set_line_numbers(ifdata_start_line_num, ifdata_end_line_num);

                                tmp_a2l() << xfiller + "/end" + xs0 + "IF_DATA" << xtail << std::endl;
                                //ifdata_segments.push_back(xsection + "/end" + xs0 + "IF_DATA" + '\n');
                                ifdata_builder.add_section(xsection + "/end" + xs0 + "IF_DATA" + '\n');
                                ifdata_builder.finalize();

                                /*
                                                        match = IF_DATA_END.match(line)
                                                        if match:
                                                            s, e = match.span()
                                                            if_data_end = (line_num, e - len(match.group("tail")))
                                                            if_data_section.append("{}/end{}IF_DATA".format(match.group("section"), match.group("s0")))
                                                            section = (
                                                                if_data_start,
                                                                if_data_end,
                                                                "\n".join(if_data_section),
                                                            )
                                                            sections.append(section)
                                                            in_if_data = False
                                                            if_data_section = []
                                                            line = "{}/end{}IF_DATA".format(" " * len(match.group("section")), match.group("s0"))
                                                            # cut_out_ifdata()
                                                            result.append(line)
                                 */
                            }
                            else {
                                ifdata_builder.add_section(line + "\n");
                                tmp_a2l() << std::endl;
                            }
                        }
                    }
                }
                else {
                    match = re_aml_end(line);
                    if (match) {
                        tmp_aml() << "/end A2ML" << std::endl;
                        tmp_a2l() << "/end A2ML" << std::endl;
                        in_aml = false;
                    }
                    else {
                        tmp_aml() << line << std::endl;
                        tmp_a2l() << std::endl;
                    }
                }
            }
        }
        else {
            throw std::runtime_error("Temporary file 'A2L_pre.tmp' could not opened; this should not happen.");
        }
        file.close();
        return IfDataReader("IFDATA.tmp", ifdata_builder);
    }

protected:
    std::string shorten_file_name(fs::path file_name) {
        if (file_name.parent_path() == fs::current_path()) {
            return file_name.filename().string();
        }
        else {
            return file_name.string();
        }
    }

    void update_line_map(const fs::path& path, std::uint64_t start_line_number) {
        auto key = shorten_file_name(path);

        if (line_map.contains(key)) {
            auto& entry = line_map[key];
            //std::cout << "\tAdd key: " << key << " " << start_line_number << " " << absolute_line_number << std::endl;
            entry.push_back(std::tuple < int, int > {start_line_number, absolute_line_number});
        }
        else {
            auto item = std::vector < LineMap::line_map_item_t >
            { std::make_tuple(start_line_number, absolute_line_number) };
            line_map[key] = item;
            //std::cout << "\tNew key: " << key << " " << start_line_number << " " << absolute_line_number << std::endl;
        }
    }

    void get_include_paths_from_env() {
#if defined(_WIN32)
        const char delimiter = ';';
#else
        const char delimiter = ':';
#endif
        char* asap_include = std::getenv("ASAP_INCLUDE");

        if (asap_include == NULL)
        {
            return;
        }

        char* ptr;
        ptr = strtok(asap_include, &delimiter);
        while (ptr != NULL)
        {
            include_paths.push_back(ptr);
            ptr = strtok(NULL, &delimiter);
        }
    }

    std::optional<fs::path> locate_file(const std::string& file_name, const std::string& additional_path) {
        std::vector<std::string> paths{};

        paths.push_back(fs::current_path().string());
        paths.push_back(additional_path);
        paths.insert(paths.end(), include_paths.begin(), include_paths.end());

        for (const auto& include_path : paths) {
            auto fn(fs::path(include_path) / fs::path(file_name));
            if (fs::exists(fn)) {
                return fn;
            }
        }
        return  std::nullopt;
    }

private:
    TempFile tmp_a2l_pre;
    TempFile tmp_a2l;
    TempFile tmp_aml;
    TempFile tmp_ifdata;

    std::vector<std::string> include_paths{};
    std::uint64_t absolute_line_number{ 0 };
    RegExp re_cpp_comment{ CPP_COMMENT };
    RegExp re_multiline_start{ MULTILINE_START };
    RegExp re_multiline_end{ MULTILINE_END };
    RegExp re_include{ INCLUDE };
    RegExp re_aml_start{ AML_START };
    RegExp re_aml_end{ AML_END };
    RegExp re_if_data_start{ IF_DATA_START };
    RegExp re_if_data_end{ IF_DATA_END };
};

#endif // __PREPROCESSOR_HPP
