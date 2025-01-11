/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023-2024 by Christoph Schueler <cpu12.gems.googlemail.com>

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
    // #define __STDC_WANT_LIB_EXT1__ (1)
    #define _CRT_SECURE_NO_WARNINGS
    #include <algorithm>
    #include <cassert>
    #include <cstdio>
    #include <cstdlib>
    #include <cstring>
    #include <filesystem>
    #include <fstream>
    #include <iostream>
    #include <iterator>
    #include <map>
    #include <optional>
    #include <regex>
    #include <tuple>
    #include <vector>

namespace fs = std::filesystem;

    #include "ifdata.hpp"
    #include "line_map.hpp"
    #include "tempfile.hpp"
    #include "token_stream.hpp"
    #include "tokenizer.hpp"
    #include "utils.hpp"
    #include "logger.hpp"


struct Filenames {
    Filenames()                 = default;
    Filenames(const Filenames&) = default;
    Filenames(Filenames&&)      = default;

    Filenames(const std::string& _a2l, const std::string& _aml, const std::string& _ifdata) :
        a2l(_a2l), aml(_aml), ifdata(_ifdata) {
    }

    std::string a2l;
    std::string aml;
    std::string ifdata;
};

using preprocessor_result_t = std::tuple<Filenames, LineMap, IfDataReader>;

class Preprocessor {
   public:

    const std::string A2L_TMP    = "A2L.tmp";
    const std::string AML_TMP    = "AML.tmp";
    const std::string IFDATA_TMP = "IFDATA.tmp";

    Preprocessor(spdlog::level::level_enum log_level) :
        tmp_a2l(A2L_TMP, true),
        tmp_aml(AML_TMP),
        tmp_ifdata(IFDATA_TMP, true),
        a2l_token_writer(tmp_a2l),
        ifdata_builder{ tmp_ifdata.handle() } {
            get_include_paths_from_env();
            m_filenames.a2l    = tmp_a2l.abs_path();
            m_filenames.aml    = tmp_aml.abs_path();
            m_filenames.ifdata = tmp_ifdata.abs_path();
            m_logger = create_logger("preprocessor", log_level);
    }

    ~Preprocessor() {
        tmp_a2l.close();
        tmp_aml.close();
        tmp_ifdata.close();
    }

    preprocessor_result_t process(const std::string& filename, const std::string& encoding) {
        _process_file(filename);
        return {
            m_filenames, line_map, IfDataReader{ m_filenames.ifdata, ifdata_builder }
        };
    }

    void finalize() {
        spdlog::shutdown();
        tmp_a2l.close();
        tmp_aml.close();
        tmp_ifdata.close();
    }

    LineMap line_map{};

   protected:

    void skip_bom(auto& fs) {
        const unsigned char boms[]{ 0xef, 0xbb, 0xbf };
        bool                have_bom{ true };
        for (const auto& c : boms) {
            if ((unsigned char)fs.get() != c)
                have_bom = false;
        }
        if (!have_bom)
            fs.seekg(0);
    }

    void _process_file(const std::string& filename) {
        std::uint64_t      start_line_number = 1;
        fs::path           path{ filename };
        auto               abs_pth = fs::absolute(path);
        std::ifstream      file(abs_pth, std::ios::binary);
        bool               begin       = false;
        bool               end         = false;
        bool               ifdata      = false;
        bool               ifdata_name = false;
        bool               collect{ false };
        bool               include     = false;
        std::uint8_t       skip_tokens = 0;
        std::vector<Token> collected_tokens{};
        bool               suppress_comments{ true };

        if (line_map.contains(abs_pth.string())) {
            throw std::runtime_error(
                "[ERROR (pya2l.Preprocessor)]  Circular "
                "dependency to include file '" +
                abs_pth.string() + "'."
            );
        }

        if (file.is_open()) {
            m_logger->info("Preprocessing and tokenizing '{}'.", filename);
            std::size_t end_line{ 0 };

            skip_bom(file);

            for (auto token : tokenizer(file)) {
                if (skip_tokens > 0) {
                    if (token.m_token_class != TokenClass::COMMENT) {
                        skip_tokens--;
                    }
                } else {
                    end_line = token.m_line_numbers.end_line;
                }
                if (token.m_token_class == TokenClass::COMMENT) {
                    const auto lines      = split(token.m_payload, '\n');
                    auto       line_count = lines.size();
                    for (const auto& line : lines) {
                        // tmp_a2l() << std::string(line.length(), ' ');
                        if (a2ml == true) {
                            if (suppress_comments) {
                                tmp_aml() << std::string(line.length(), ' ');
                            } else {
                                tmp_aml() << line;
                            }
                        }
                        if (--line_count > 0) {
                            // tmp_a2l() << std::endl;
                            if (a2ml == true) {
                                tmp_aml() << std::endl;
                            }
                        }
                    }
                } else if ((token.m_token_class == TokenClass::REGULAR) || (token.m_token_class == TokenClass::STRING)) {
                    if (end == true) {
                        if (token.m_payload == "A2ML") {
                            a2ml = false;
                            //                     tmp_aml() << token.m_payload;
                            for (const auto& item : collected_tokens) {
                                // tmp_a2l() << item.m_payload;
                                a2l_token_writer << item;
                                // tmp_aml() << item.m_payload;
                            }
                            tmp_aml() << "A2ML";
                        } else if (token.m_payload == "IF_DATA") {
                            ifdata = false;
                            ifdata_builder.add_token(token);
                            ifdata_builder.finalize();
                            for (const auto& item : collected_tokens) {
                                // tmp_a2l() << item.m_payload;
                                a2l_token_writer << item;
                            }
                        } else {
                            for (const auto& item : collected_tokens) {
                                if (item.m_token_class == TokenClass::REGULAR) {
                                    // tmp_a2l() << std::string(item.m_payload.length(), ' ');
                                } else if (item.m_token_class == TokenClass::WHITESPACE) {
                                    // tmp_a2l() << item.m_payload;
                                    // a2l_token_writer << item;
                                }
                            }
                        }
                        collected_tokens.clear();
                        collect = false;
                        end     = false;
                    }
                    if (a2ml == true) {
                        if (token.m_token_class == TokenClass::STRING) {
                            tmp_aml() << "\"" << token.m_payload << "\"";
                        } else {
                            tmp_aml() << token.m_payload;
                        }
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
                            end     = true;
                        }
                    }
                    if (include == true) {
                        auto _fn = token.m_payload;

                        if (const auto incl_file = locate_file(_fn, path.parent_path().string()); incl_file.has_value()) {
                            const auto length = (end_line - start_line_number);
                            update_line_map(abs_pth, line_offset, line_offset + length - 1, start_line_number, end_line - 1);
                            line_offset += length;
                            m_logger->info("Including '{}'.", incl_file.value().string());
                            _process_file(incl_file.value().string());
                        } else {
                            throw std::runtime_error(
                                "[ERROR (pya2l.Preprocessor)]  Could "
                                "not locate include file '" +
                                _fn + "'."
                            );
                        }
                        include = false;
                        line_offset++;
                        start_line_number = token.m_line_numbers.end_line + 1;
                        skip_tokens       = 2;
                    }
                    if (token.m_payload == "/include") {
                        include = true;
                    }
                    if (ifdata == true || a2ml == true) {
                        if (end == false) {
                            if (ifdata_name == true) {
                                // tmp_a2l() << token.m_payload;
                                a2l_token_writer << token;
                                ifdata_name = false;
                            } else {
                                // tmp_a2l() << std::string(token.m_payload.length(), ' ');
                            }
                        }
                    } else {
                        if ((include == false) && (skip_tokens == 0)) {
                            // tmp_a2l() << token.m_payload;
                            a2l_token_writer << token;
                        }
                    }
                    if (begin) {
                        begin   = false;
                        collect = false;
                        collected_tokens.push_back(token);
                        if (token.m_payload == "A2ML") {
                            a2ml = true;
                            for (const auto& item : collected_tokens) {
                                tmp_aml() << item.m_payload;
                            }
                        } else if (token.m_payload == "IF_DATA") {
                            ifdata      = true;
                            ifdata_name = true;
                            for (const auto& item : collected_tokens) {
                                ifdata_builder.add_token(item);
                            }
                        }
                        collected_tokens.clear();
                    }
                    if ((token.m_payload == "/begin") && (ifdata == false)) {
                        begin   = true;
                        collect = true;
                        collected_tokens.push_back(token);
                    }
                } else if (token.m_token_class == TokenClass::WHITESPACE) {
                    if ((end == false) && (include == false) && (skip_tokens == 0)) {
                        // tmp_a2l() << token.m_payload;
                        // a2l_token_writer << token;
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
            const auto length = (end_line - start_line_number);
            update_line_map(abs_pth, line_offset, line_offset + length, start_line_number, end_line);
            line_offset += length;
        } else {
            throw std::runtime_error("Could not open file: '" + abs_pth.string() + "'");
        }
    }

    std::string shorten_file_name(fs::path file_name) {
        if (file_name.parent_path() == fs::current_path()) {
            return file_name.filename().string();
        } else {
            return file_name.string();
        }
    }

    void update_line_map(
        const fs::path& path, std::uint64_t abs_start, std::uint64_t abs_end, std::uint64_t rel_start, std::uint64_t rel_end
    ) {
        const auto key = shorten_file_name(path);
        line_map.add_entry(path.string(), abs_start, abs_end, rel_start, rel_end);
    }

    void get_include_paths_from_env() {
        const auto var = get_env_var("ASAP_INCLUDE");
        include_paths  = split_path(var);
    }

    std::optional<fs::path> locate_file(const std::string& file_name, const std::string& additional_path) {
        std::vector<std::string> paths{};

        paths.push_back(fs::current_path().string());
        paths.push_back(additional_path);
        paths.insert(paths.end(), include_paths.begin(), include_paths.end());

        for (const auto& include_path : paths) {
            const auto fn(fs::path(include_path) / fs::path(file_name));
            if (fs::exists(fn)) {
                return fn;
            }
        }
        return std::nullopt;
    }

   private:

    std::shared_ptr<spdlog::logger>    m_logger;
    TempFile                 tmp_a2l;
    TempFile                 tmp_aml;
    TempFile                 tmp_ifdata;
    TokenWriter              a2l_token_writer;
    IfDataBuilder            ifdata_builder;
    Filenames                m_filenames{};
    std::vector<std::string> include_paths{};
    std::size_t              line_offset{ 1 };
    bool                     a2ml{ false };
};

#endif  // __PREPROCESSOR_HPP
