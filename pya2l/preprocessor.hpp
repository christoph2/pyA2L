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
enum class CollectionType : std::uint8_t {
    NONE,
    A2l,
    AML,
    IFDATA
};
*/

class Preprocessor {
public:

    const std::string A2L_TMP = "A2L.tmp";
    const std::string AML_TMP = "AML.tmp";
    const std::string IFDATA_TMP = "IFDATA.tmp";

    Preprocessor(const std::string& loglevel) : tmp_a2l(A2L_TMP), tmp_aml(AML_TMP), tmp_ifdata(IFDATA_TMP, true), ifdata_builder{tmp_ifdata.handle()} {
        get_include_paths_from_env();
        //tmp_a2l.to_stdout();
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
        std::uint64_t start_line_number = 1;
        fs::path path{ filename };
        auto abs_pth = fs::absolute(path);
        std::ifstream file(abs_pth);
        bool begin = false;
        bool end = false;
        bool a2ml = false;
        bool ifdata = false;
        bool collect { false };
        bool include = false;
        std::uint8_t skip_tokens = 0;
        std::vector<Token> collected_tokens{};

        if (line_map.contains(abs_pth.string())) {
            throw std::runtime_error("[ERROR (pya2l.Preprocessor)]: Circular dependency to include file '" + abs_pth.string() + "'.");
        }

        if (file.is_open()) {
            std::cout << "[INFO (pya2l.Preprocessor)]: Preprocessing '" + filename + "'." << std::endl;
            std::size_t end_line{ 0 };

            for (const auto&& token : tokenizer(file)) {
                end_line = token.m_line_numbers.end_line;
                if (skip_tokens > 0) {
                    skip_tokens--;
                }
                if (token.m_token_type == TokenType::COMMENT) {
                    auto lines = split(token.m_payload, '\n');
                    auto line_count = lines.size();
                    for (auto&& line : lines) {
                        tmp_a2l() << std::string(line.length(), ' ');
                        if (a2ml == true) {
                            tmp_aml() << std::string(line.length(), ' ');
                        }
                        if (--line_count > 0) {
                            tmp_a2l() << std::endl;
                            if (a2ml == true) {
                                tmp_aml() << std::endl;
                            }
                        }
                    }
                } else if (token.m_token_type == TokenType::REGULAR) {
                    if (end == true) {
                        if (token.m_payload == "A2ML") {
                            a2ml = false;
                            tmp_aml() << token.m_payload;
                            for (auto&& item : collected_tokens) {
                                tmp_a2l() << item.m_payload;
                            }
                        } else if (token.m_payload == "IF_DATA") {
                            ifdata = false;
                            ifdata_builder.add_token(token);
                            ifdata_builder.finalize();
                            for (auto&& item : collected_tokens) {
                                tmp_a2l() << item.m_payload;
                            }
                        } else {
                            for (auto&& item : collected_tokens) {
                                if (item.m_token_type == TokenType::REGULAR) {
                                    tmp_a2l() << std::string(item.m_payload.length(), ' ');
                                } else if (item.m_token_type == TokenType::WHITESPACE) {
                                    tmp_a2l() << item.m_payload;
                                }
                            }
                        }
                        collected_tokens.clear();
                        collect = false;
                        end = false;
                    }
                    if (a2ml == true) {
                        tmp_aml() << token.m_payload;
                        if (token.m_payload == "/end") {
                            end = true;
                            collected_tokens.push_back(token);
                            collect = true;
                        }
                    } else if (ifdata == true) {
                        ifdata_builder.add_token(token);
                        if (token.m_payload == "/end") {
                            collected_tokens.push_back(token);
                            collect = true;
                            end = true;
                        }
                    }
                    if (include == true) {
                        auto _fn = token.m_payload.substr(1, token.m_payload.length() - 2);
                        auto incl_file = locate_file(_fn, path.parent_path().string());

                        if (incl_file.has_value()) {
                            update_line_map(abs_pth, start_line_number);
                            auto length = (end_line - start_line_number);
                            std::cout << "\t[ " << abs_pth.string() << ": " << line_offset << " " << line_offset + length - 1 << " " << start_line_number << " " << token.m_line_numbers.start_line - 1 << " ]" << std::endl;
                            //line_offset += token.m_line_numbers.end_line;
                            line_offset += length;

                            std::cout << "[INFO (pya2l.Preprocessor)]: Including '" + incl_file.value().string() + "'." << std::endl;
                            _process_file(incl_file.value().string());
                        }
                        else {
                            throw std::runtime_error("[ERROR (pya2l.Preprocessor)]: Could not locate include file '" + _fn + "'.");
                        }
                        include = false;                  
                        start_line_number = token.m_line_numbers.end_line + 1;
                        skip_tokens = 2;
                    }
                    if (token.m_payload == "/include") {
                        include = true;
                    }
                    if (ifdata == true || a2ml == true) {
                        if (end == false) {
                            tmp_a2l() << std::string(token.m_payload.length(), ' ');
                        }
                    } else {
                        if ((include == false) && (skip_tokens == 0)) {
                            tmp_a2l() << token.m_payload;
                        }
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
                                ifdata_builder.add_token(item);
                            }
                        }
                        collected_tokens.clear();
                    }
                    if ((token.m_payload == "/begin") && (ifdata == false)) {
                        begin = true;
                        collect = true;
                        collected_tokens.push_back(token);
                    }
                } else if (token.m_token_type == TokenType::WHITESPACE) {
                    if ((end == false) && (include == false) && (skip_tokens == 0)) {
                        tmp_a2l() << token.m_payload;
                    }
                    if (collect == true) {
                        collected_tokens.push_back(token);
                    }
                    if (a2ml == true) {
                        tmp_aml() << token.m_payload;
                    } else if (ifdata == true) {
                        ifdata_builder.add_token(token);
                    }
                }
            }
            update_line_map(abs_pth, start_line_number);
            auto length = (end_line - start_line_number);
            std::cout << "\t[ " << abs_pth.string() << ": " << line_offset << " " << line_offset + length - 1 << " " << start_line_number << " " << end_line - 1 << " ]" << std::endl;
            //line_offset += end_line;
            line_offset += length;
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

    void update_line_map(const fs::path& path, std::uint64_t abs_start, std::uint64_t abs_end, std::uint64_t rel_start, std::uint64_t rel_end) {
        auto key = shorten_file_name(path);

        if (line_map.contains(key)) {
            auto& entry = line_map[key];
            //std::cout << "\tAdd key: " << key << " " << start_line_number << " " << absolute_line_number << std::endl;
            
            entry.push_back(std::tuple <decltype(start_line_number), decltype(line_offset)> {start_line_number, line_offset});
        }
        else {
            auto item = std::vector < LineMap::line_map_item_t > { std::make_tuple(start_line_number, line_offset) };
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
    Filenames m_filenames{};
    std::vector<std::string> include_paths{};
    std::size_t line_offset{ 1 };
};

#endif // __PREPROCESSOR_HPP
