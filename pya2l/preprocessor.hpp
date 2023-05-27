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
#include "extensions/tokenizer.hpp"


struct Filenames {

    Filenames() = default;
    Filenames(const Filenames&) = default;
    Filenames(Filenames&&) = default;
    Filenames(const std::string& _a2l, const std::string& _aml, const std::string& _ifdata) : a2l(_a2l), aml(_aml), ifdata(_ifdata) {}

    std::string a2l;
    std::string aml;
    std::string ifdata;
};

/*
struct PreprocessorResult {

    PreprocessorResult() = default;
    PreprocessorResult(const PreprocessorResult&) = default;
    PreprocessorResult(PreprocessorResult&&) = default;
    PreprocessorResult(const Filenames& f, const LineMap& m, const IfDataReader& r) : filenames(f), line_map(m), ifdata_reader(r) {}

    Filenames filenames{};
    LineMap line_map{};
    IfDataReader ifdata_reader{};
};
*/

class Preprocessor {
public:

    const std::string A2L_TMP = "A2L.tmp";
    const std::string AML_TMP = "AML.tmp";
    const std::string IFDATA_TMP = "IFDATA.tmp";

    Preprocessor(const std::string& loglevel) : tmp_a2l(A2L_TMP), tmp_aml(AML_TMP), tmp_ifdata(IFDATA_TMP, true), ifdata_builder{ tmp_ifdata.handle() } {
        get_include_paths_from_env();
        m_filenames.a2l = tmp_a2l.abs_path();
        m_filenames.aml = tmp_aml.abs_path();
        m_filenames.ifdata = tmp_ifdata.abs_path();
    }

    ~Preprocessor() {

    }

    std::tuple<Filenames, LineMap, IfDataReader> process(const std::string& filename, const std::string& encoding) {
        _process_file(filename);
        line_map.finalize();
        {
            return std::tuple<Filenames, LineMap, IfDataReader>(m_filenames, line_map, {});
        }
    }

    LineMap line_map{};

protected:
    void _process_file(const std::string& filename) {
        //std::uint64_t start_line_number = absolute_line_number + 1;
        fs::path path{ filename };
        auto abs_pth = fs::absolute(path);
        std::ifstream file(abs_pth);
        bool begin = false;
        bool a2ml = false;
        bool ifdata = false;
        bool collect = false;
        bool include = false;
        std::vector<Token> collected_tokens{};

        if (line_map.contains(abs_pth.string())) {
            throw std::runtime_error("[ERROR (pya2l.Preprocessor)]: Circular dependency to include file '" + abs_pth.string() + "'.");
        }

        if (file.is_open()) {
            std::cout << "[INFO (pya2l.Preprocessor)]: Preprocessing '" + filename + "'." << std::endl;
            for (const auto&& token : tokenizer(file)) {
                //std::cout << token.m_payload << " [" << token.m_line_numbers.start_line << ", " <<
                //    token.m_line_numbers.start_col << ", " << token.m_line_numbers.end_line << ", " << token.m_line_numbers.end_col << "]" << std::endl;
                if (token.m_token_type == TokenType::COMMENT) {
                    auto lines = split(token.m_payload, '\n');
                    auto line_count = lines.size();
                    for (auto&& line : lines) {
                        std::cout << std::string(line.length(), ' ');
                        if (a2ml == true) {
                            tmp_aml() << std::string(line.length(), ' ');
                        }
                        if (--line_count > 0) {
                            std::cout << std::endl;
                            if (a2ml == true) {
                                tmp_aml() << std::endl;
                            }
                        }
                    }
                } else if (token.m_token_type == TokenType::REGULAR) {
                    if (a2ml == true) {
                        tmp_aml() << token.m_payload;
                        if (token.m_payload == "/end") {
                            tmp_aml() << " A2ML";
                            a2ml = false;
                        }
                    } else if (ifdata == true) {
                        //tmp_ifdata() << token.m_payload;
                        ifdata_builder.add_token(token);
                        if (token.m_payload == "/end") {
                            //tmp_ifdata() << " IF_DATA";
                            // ifdata_builder.add_token(item);  // TODO: IMPL!!!
                            ifdata = false;
                            ifdata_builder.finalize();
                        }
                    } else if (include == true) {
                        auto incl_file = locate_file(token.m_payload.substr(1, token.m_payload.length() - 2), path.parent_path().string());

                        if (incl_file.has_value()) {

                        } else {
                            throw std::runtime_error("[ERROR (pya2l.Preprocessor)]: Could not locate include file '" + file_name + "'.");
                        }
                        include = false;
                    }
                    if (ifdata == true || a2ml == true) {
                        std::cout << std::string(token.m_payload.length(), ' ');
                    } else {
                        std::cout << token.m_payload;
                    }
                    if (begin) {
                        begin = false;
                        collect = false;
                        collected_tokens.push_back(token);
                        if (token.m_payload == "A2ML") {
                            a2ml = true;
                            for (auto& item : collected_tokens) {
                                tmp_aml() << item.m_payload;
                            }
                        } else if (token.m_payload == "IF_DATA") {
                            ifdata = true;
                            for (auto& item : collected_tokens) {
                                //tmp_ifdata() << item.m_payload;
                                ifdata_builder.add_token(item);
                            }
                        }
                        collected_tokens.clear();
                    }
                    if (token.m_payload == "/begin") {
                        begin = true;
                        collect = true;
                        collected_tokens.push_back(token);
                    } else if (token.m_payload == "/include") {
                        include = true;
                    }
                } else if (token.m_token_type == TokenType::WHITESPACE) {
                    std::cout << token.m_payload;
                    if (a2ml == true) {
                        tmp_aml() << token.m_payload;
                    } else if (ifdata == true) {
                        //tmp_ifdata() << token.m_payload;
                        ifdata_builder.add_token(token);
                    } else if (collect == true) {
                        collected_tokens.push_back(token);
                    }

                }
            }
        } else {
            throw std::runtime_error("Could not open file: '" + abs_pth.string() + "'");
        }
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
            entry.push_back(std::tuple <decltype(start_line_number), decltype(absolute_line_number)> {start_line_number, absolute_line_number});
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
    TempFile tmp_a2l;
    TempFile tmp_aml;
    TempFile tmp_ifdata;
    IfDataBuilder ifdata_builder;

	std::size_t absolute_line_number;
    Filenames m_filenames{};
    std::vector<std::string> include_paths{};
};

#endif // __PREPROCESSOR_HPP
