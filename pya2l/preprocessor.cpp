/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2023 by Christoph Schueler <cpu12.gems@googlemail.com>

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

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "preprocessor.hpp"

namespace fs = std::filesystem;

const std::regex CPP_COMMENT("(?://)(.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_START("(?:/\\*)(.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_END("(?:\\*/)(.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex INCLUDE("^(?:\\s*)/include\\s+\"([^\"]*)\"", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex AML_START("^\\s*/begin\\s+A[23]ML(.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex AML_END("^\\s*/end\\s+A[23]ML", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_START("/begin(\\s+)IF_DATA(\\s+)(\\S*)(.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_END("^(.*?)/end(\\s+)IF_DATA(.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);


/*
 * strip `std::string` from end (in place).
 */
static inline void rstrip(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

/*
 * Cut out section of text and replace it with a single space.
 */
void blank_out(std::string& text, std::int32_t start, std::int32_t end)
{
    if (end == -1) {
        text.resize(start);
    } else {
        text.erase(text.begin() + start, text.begin() + end);
    }
    rstrip(text);
}

class RegExp {
public:

    RegExp(const std::regex& pattern) : m_pattern(pattern), m_match{} {
    }

    bool operator()(const std::string& text) {
        m_matched = std::regex_search(text, m_match, m_pattern);
        //std::cout << "Matchie pos: " << m_match.position(0) << ": " << text << '\n';
        return m_matched;
    }

    int pos(int idx) const {
        return m_match.position(idx);
    }

    int start(int idx) const {
        return pos(idx);
    }

    int end(int idx) const {
        return m_match.position(idx) + m_match.length(idx) ;
    }

    std::tuple<int, int> span(int idx) const {
        return std::make_tuple(start(idx), end(idx));
    }

    auto str(int idx) const {
        return m_match.str(idx);
    }

    auto prefix() const {
        return m_match.prefix().str();
    }

    auto suffix() const {
        return m_match.suffix().str();
    }

private:
    std::regex m_pattern;
    std::smatch m_match;
    bool m_matched {false};
};


class LineMap {
public:

    using line_map_item_t = std::tuple<int, int>;
    using line_map_t = std::map<std::string, std::vector<line_map_item_t>>;

    LineMap() : m_line_map() {
    }

    int contains(const std::string& key) const {
        return m_line_map.contains(key);
    }

    std::vector<line_map_item_t>& operator[](const std::string& key) {
        return m_line_map[key];
    }

    std::optional<std::tuple<std::string, std::size_t>> lookup(std::size_t line_no) {
        auto idx = search_offset(line_no);

        if (idx.has_value()) {

            auto [abs_start, abs_end, rel_start, rel_end, name] = items[idx.value()];
            std::int32_t offset = (abs_start - rel_start) - 1;
            std::cout << "\tline_no: " << line_no /* - offset */ << " offset: " << offset << " name: " << name <<  " abs_start: " << abs_start << " rel_start: " << rel_start  << '\n';
            return std::tuple<std::string, std::size_t>(name, line_no - offset);
        } else {
            std::cout << "line_no: " << line_no << " not found\n";
            return std::nullopt;
        }

    }

    void finalize() {
        std::size_t  offset {0};
        std::vector<std::tuple<std::size_t, std::size_t, std::string>> sections;
        std::map<std::string, std::size_t> offsets;

        for (const auto& [k, v] : m_line_map) {
            offsets[k] = 1;

        }
        for (const auto& [k, v] : m_line_map) {
            for (const auto& [start, end] : v) {
                sections.push_back(std::make_tuple(start, end, k));
            }
        }
        std::sort(sections.begin(), sections.end(), [](auto& lhs, auto& rhs) {
            return std::get<0>(lhs) < std::get<0>(rhs);
        });

        std::size_t length {0};
        for (auto [start, end, name]: sections) {
            length = end - start;
            start_offsets.push_back(start);
            offset = offsets[name];
            offsets[name] = length + offset;
            last_line_no = end;
            items.push_back(std::make_tuple(start, end, offset, length + offset, name));
        }
        for (auto [abs_start, abs_end, rel_start, rel_end, name]: items) {
            std::cout << "[" << name << "] " << abs_start << " "  << abs_end << " "  << rel_start << " " << rel_end << " " <<   std::endl;
        }

    }

private:

    std::optional<std::size_t> search_offset(std::size_t key) const {
        std::size_t left {0}, mid{0}, right{std::size(start_offsets)};

        if (key > last_line_no) {
            return std::nullopt;
        }
        while (left < right) {
            mid = left + (right - left) / 2;
            if (key == start_offsets[mid]) {
                return mid;
            } else if (key < start_offsets[mid]) {
                right = mid;
            } else {
                left = mid + 1;
            }
        }
        return left - 1;
    }

    line_map_t m_line_map {};
    std::vector<size_t> start_offsets {};
    std::size_t last_line_no {0};
    std::vector<std::tuple<std::size_t, std::size_t, std::size_t, std::size_t, std::string>> items {};
};

/*
 * Create ofstream object and delete on d-tor (or using 'remove()').
 */
class TempFile {
public:

    TempFile(const std::string& path, bool binary = false) :
        m_path(fs::path(path)), m_file(path, std::ios::trunc | std::ios::out | (binary? std::ios::binary : std::ios::out))  {
    }

    TempFile() = delete;

    ~TempFile() {
        remove();
    }

    std::ofstream& operator()() {
        return m_file;
    }

    void close()
    {
        if (m_file.is_open()) {
            m_file.close();
        }
    }

    void remove() {
        if (fs::exists(m_path)) {
            close();
            //fs::remove(m_path);
        }
    }

private:

    fs::path m_path;
    std::ofstream m_file;
};

// clang++ -Wall -ggdb -std=c++20 preprocessor.cpp -o preprocessor.exe

class Preprocessor {
public:

    Preprocessor() : tmp_a2l_pre("A2L_pre.tmp"), tmp_a2l("A2L.tmp"), tmp_aml("AML.tmp"), tmp_ifdata("IFDATA.tmp", true) {
        get_include_paths_from_env();
    }

    ~Preprocessor() {
        //line_map.finalize();
    }

    LineMap line_map {};

//protected:
    void _process_file(const std::string& filename) {
        std::uint64_t start_line_number = absolute_line_number + 1;
        fs::path path {filename};
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
                        printf("%s\n", rl.c_str());
                        tmp_a2l_pre() << rl << std::endl;
                        continue;
                    } else {
                        rl = "\n";
                        printf("\n");
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
                    } else {
                        use_c_match = true;
                    }
                } else if (c_match) {
                    use_c_match = true;
                } else if (cpp_match) {
                    use_cpp_match = true;
                }
                if (use_cpp_match) {
                    rl = re_cpp_comment.prefix();
                } else if (use_c_match) {
                    match = re_multiline_end(line);
                    if (match) {
                        multi_line = false;
                        blank_out(line, re_multiline_start.start(0), re_multiline_end.start(1));
                        rl = line;
                    } else {
                        multi_line = true;
                        blank_out(line, re_multiline_start.start(0), -1);
                        rl = line;
                    }
                } else {
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
                    } else {
                        throw std::runtime_error("Can't find include file: '" + include_file_name + "'");
                    }
                } else {
                    escape_string(rl);
                    printf("%s\n", rl.c_str());
                    tmp_a2l_pre() << rl <<  std::endl;
                }
            }
            update_line_map(abs_pth, start_line_number);
            file.close();
        } else {
            throw std::runtime_error("Could not open file: '" + abs_pth.string() + "'");
        }
    }

    void _process_aml() {
        bool in_aml = false;
        bool in_if_data = false;
        std::uint64_t line_num = 0;

        const auto cut_out_ifdata = [&in_aml, &in_if_data, &line_num](const std::string& line) -> void {
            //std::cout << line_num << std::endl;
        };

        std::ifstream file("A2L_pre.tmp");
        //std::cout << "Before AML" << std::endl;
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
                        // aml_section.append("/begin A2ML")
                        printf("/begin A2ML [%u]\n", line_num);
                        tmp_aml() << "/begin A2ML" << std::endl;
                    } else {
                        if (!in_if_data) {
                            cut_out_ifdata(line);

                        } else {
                            match = re_if_data_end(line);
                            if (match) {
                                auto [start, end] = re_if_data_end.span(0);
                                in_if_data = false;
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
                            } else {
                                // if_data_section.append(line.strip())
                                //result.append("")
                                printf("\n");
                            }
                        }
                    }
                } else {
                    match = re_aml_end(line);
                    if (match) {
                        printf("/end A2ML [%u]\n", line_num);
                        tmp_aml() << "/end A2ML" << std::endl;
                        in_aml = false;
                    } else {
                        tmp_aml() << line << std::endl;
                    }
/*
 match = AML_END.match(line)
                if match:
                    aml_section.append("/end A2ML ")
                    line = ""
                    in_aml = False
                else:
                    aml_section.append(line)
                result.append("")
 */
                }
                //cut_out_ifdata(line);
            }
        } else {
            throw std::runtime_error("Temporary file 'A2L.tmp' could not opened; this should not happen.");
        }
        file.close();
        //std::cout << "After AML" << std::endl;
    }

protected:
    std::string shorten_file_name(fs::path file_name) {
        if (file_name.parent_path() == fs::current_path()) {
            return file_name.filename().string();
        } else {
            return file_name.string();
        }
    }

    void update_line_map(const fs::path& path, std::uint64_t start_line_number) {
        auto key = shorten_file_name(path);

        if (line_map.contains(key)) {
            auto& entry = line_map[key];
            //std::cout << "\tAdd key: " << key << " " << start_line_number << " " << absolute_line_number << std::endl;
            entry.push_back(std::tuple < int, int > {start_line_number, absolute_line_number});
        } else {
            auto item = std::vector < LineMap::line_map_item_t >
                        {std::make_tuple(start_line_number, absolute_line_number)};
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
        char * asap_include = std::getenv("ASAP_INCLUDE");

        if (asap_include == NULL)
        {
            return;
        }

        char *ptr;
        ptr = strtok(asap_include, &delimiter);
        while (ptr != NULL)
        {
            include_paths.push_back(ptr);
            ptr = strtok (NULL, &delimiter);
        }
    }

    std::optional<fs::path> locate_file(const std::string& file_name, const std::string& additional_path) {
        std::vector<std::string> paths {};

        paths.push_back(fs::current_path().string());
        paths.push_back(additional_path);
        paths.insert(paths.end(), include_paths.begin(), include_paths.end());

        for (const auto& include_path : paths) {
            auto fn (fs::path(include_path) / fs::path(file_name));
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

    std::vector<std::string> include_paths {};
    std::uint64_t absolute_line_number {0};
    RegExp re_cpp_comment {CPP_COMMENT};
    RegExp re_multiline_start {MULTILINE_START};
    RegExp re_multiline_end {MULTILINE_END};
    RegExp re_include {INCLUDE};
    RegExp re_aml_start {AML_START};
    RegExp re_aml_end  {AML_END};
    RegExp re_if_data_start  {IF_DATA_START};
    RegExp re_if_data_end  {IF_DATA_END};
};

enum class State: std::uint8_t {
    IDLE,
    IN_STRING,
};

/*
 * Replace pesky A2L string ""escapes"" by the usual C/C++ \" version.
 */
void escape_string(std::string& line) {
    State state  {State::IDLE};
    std::size_t pos = line.find('"', 0);
    const std::size_t length = std::size(line);

    if (length == 0 || std::string::npos == pos) {
        return; // Nothing to do.
    }
    state = State::IN_STRING;
    pos += 1;
    while (true) {
        pos = line.find('"', pos);
        switch (state) {
            case State::IDLE:
                if (std::string::npos == pos) {
                    return; // We're done.
                } else {
                    state = State::IN_STRING;
                }
                break;
            case State::IN_STRING:
                if (std::string::npos == pos) {
                    // unterminated string -- don't handle, i.e. hand-over to ANTLR.
                    return;
                }
                if (pos == length - 1) {
                    return; // Line completly processed.
                }
                if (line[pos + 1] == '"' && line[pos - 1] != '\x5c') {
                    line[pos] = '\x5c';
                    state = State::IN_STRING;
                    pos += 2;
                } else {
                    state = State::IDLE;
                    pos += 1;
                }
                break;
        }
    }
}

void ld(Preprocessor& p, std::size_t line_no)
{
    auto res = p.line_map.lookup(line_no);
    if (res.has_value()) {
        auto [name, num] = res.value();
        std::cout << "\t\t[" << name << "] " << num << std::endl;
    } else {
        std::cout << line_no << " not found!" << std::endl;
    }
}

int main(int argc, char** argv)
{
    Preprocessor p;

    if (argc > 1) {
        p._process_file(argv[1]);
        p._process_aml();
    } else {
        //p._process_file("ASAP2_Demo_V161.a2l");
        p._process_file("comments.txt");

        p.line_map.finalize();

        ld(p, 1);
        ld(p, 3);
        ld(p, 4);
        ld(p, 8);
        ld(p, 12);
        ld(p, 13);
        p._process_aml();

        //ld(p, 1079);
        //ld(p,1080);
        //ld(p,1081);
        //ld(p,1095);
        //ld(p,10900);


    }
    return 0;
}
