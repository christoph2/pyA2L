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
#include <regex>
#include <tuple>
#include <vector>

#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "preprocessor.hpp"

const std::regex CPP_COMMENT("(?://)(.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_START("(?:/\\*)(.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_END("(?:\\*/)(.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex INCLUDE("^(?:\\s*)/include\\s+\"([^\"]*)\"", std::regex_constants::ECMAScript | std::regex_constants::optimize);

#if 0
const std::regex AML_START("^\\s*/begin\\s+A[23]ML(?P<section>.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex AML_END("^\\s*/end\\s+A[23]ML", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_START("/begin(?P<s0>\\s+)IF_DATA(?P<s1>\\s+)(?P<section>\\S*)(?P<tail>.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_END("^(?P<section>.*?)/end(?P<s0>\\s+)IF_DATA(?P<tail>.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
#endif

namespace fs = std::filesystem;

using line_map_item_t = std::tuple<int, int>;
using line_map_t = std::map<std::string, std::vector<line_map_item_t>>;

/*
 * strip from start (in place).
 */
static inline void lstrip(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](unsigned char ch) {
        return !std::isspace(ch);
    }));
}

/*
 * strip from end (in place).
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

    RegExp(const std::regex& pattern) : m_pattern(pattern) {
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

class StringProcessor {

public:

private:

};

/*
 * Create ofstream object and delete on d-tor.
 */
class TempFile {
public:

    TempFile(const std::string& path) : m_path(fs::path(path)), m_file(path)  {
        if (!m_file.is_open()) {
            remove();
        } else {
            throw std::runtime_error("Could not open file: '" + m_path.string() + "'");
        }
    }

    TempFile() = delete;

    ~TempFile() {
        if (fs::exists(m_path)) {
            remove();
        }
    }

    std::ofstream& operator()() {
        return m_file;
    }

    void remove() const {
        fs::remove(m_path);
    }

private:

    fs::path m_path;
    std::ofstream m_file;
};

// clang++ -Wall -ggdb -std=c++20 preprocessor.cpp -o preprocessor.exe

class Preprocessor {
public:

    Preprocessor() {
        get_include_paths_from_env();
    }

//protected:
    void _process_file(const std::string& filename) {
        std::uint64_t start_line_number = absolute_line_number + 1;
        fs::path path {filename};
        auto abs_pth = fs::absolute(path);
        std::vector<line_map_t> lines;

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
            bool incl = false;

            std::vector<std::string> result;
            std::string rl;

            while (!file.eof()) {
                line_num++;
                absolute_line_number++;
                std::getline(file, line);
                rstrip(line);
                if (multi_line) {
                    match = re_multiline_end(line);
                    if (match) {
                        multi_line = false;
                        rl = re_multiline_end.str(1);
                        printf("%s\n", rl.c_str());
                        continue;
                    } else {
                        rl = "\n";
                        printf("\n");
                        continue;
                    }
                }
                cpp_match = re_cpp_comment(line);
                c_match = re_multiline_start(line);
                use_c_match = use_cpp_match = false;
                //printf("[%u]\tC?: %u <%u> CPP: %u <%u>\n", line_num, c_match, re_multiline_start.start(0), cpp_match, re_cpp_comment.start(0));
                incl = false;
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
                    //printf("%s\n", re_cpp_comment.prefix().c_str());
                } else if (use_c_match) {
                    match = re_multiline_end(line);
                    if (match) {
                        multi_line = false;
                        blank_out(line, re_multiline_start.start(0), re_multiline_end.start(1));
                        rl = line;
                        //printf("%s\n", rl.c_str());
                    } else {
                        multi_line = true;
                        blank_out(line, re_multiline_start.start(0), -1);
                        rl = line;
                        //printf("%s\n", rl.c_str());
                    }
                } else {
                    rl = line;
                    //printf("%s\n", line.c_str());
                }

                match = re_include(rl);
                if (match) {
                    std::string include_file_name = re_include.str(1);
                    auto where = locate_file(include_file_name, abs_pth.parent_path().string());

                    if (where.has_value()) {
                        auto key = shorten_file_name(abs_pth);
                        printf("\tS: %llu E: %llu\n", start_line_number, absolute_line_number);
                        if (line_map.contains(key)) {
                            printf("Key %s found!!!\n", key.c_str());
                            auto entry = line_map[key];
                            entry.push_back(std::tuple<int, int> {start_line_number, absolute_line_number});
                        } else {
                            printf("Key %s NOT found!!!\n", key.c_str());
                            auto item = std::vector<line_map_item_t>{ std::make_tuple(start_line_number, absolute_line_number) };
                            line_map[key] = item;
                        }
                        _process_file(where.value().string());
                        start_line_number = absolute_line_number + 1;

                    } else {
                        throw std::runtime_error("Can't find include file: '" + include_file_name + "'");
                    }
                } else {
                    printf("%s\n", rl.c_str());
                }

            }
            file.close();
        } else {
            throw std::runtime_error("Could not open file: '" + abs_pth.string() + "'");
        }
    }

protected:
    std::string shorten_file_name(fs::path file_name) {
        if (file_name.parent_path() == fs::current_path()) {
            return file_name.filename().string();
        } else {
            return file_name.string();
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
            std::cout << fn.string() << std::endl;
            if (fs::exists(fn)) {
                return fn;
            }
        }
        return  std::nullopt;
}

private:
    line_map_t line_map {};
    std::vector<std::string> include_paths {};
    std::uint64_t absolute_line_number {0};
    RegExp re_cpp_comment {CPP_COMMENT};
    RegExp re_multiline_start {MULTILINE_START};
    RegExp re_multiline_end {MULTILINE_END};
    RegExp re_include {INCLUDE};
};

enum class State: std::uint8_t {
    IDLE,
    IN_STRING,
    OPEN_QUOTE,
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
                if (line[pos + 1] == '"') {
                    line[pos] = '\x5c';
                    state = State::OPEN_QUOTE;
                    pos += 2;
                } else {
                    state = State::IDLE;
                    pos += 1;
                }
                break;
            case State::OPEN_QUOTE:
                if (line[pos + 1] == '"') {
                    // OK, quote properly closed.
                    line[pos] = '\x5c';
                    pos += 2;
                    state = State::IN_STRING;
                } else {
                    // Unterminated quote.
                    state = State::IDLE;
                }
                break;
        }
    }
}

int main(void)
{
#if 0
    std::string s = "Some people, when confronted with a problem, think "
                    "\"I know, I'll use regular expressions.\" "
                    "Now they have two problems.";

    std::regex self_regex("REGULAR EXPRESSIONS",
                          std::regex_constants::ECMAScript | std::regex_constants::icase);
    if (std::regex_search(s, self_regex)) {
        std::cout << "Text contains the phrase 'regular expressions'\n";
    }

    std::regex word_regex("(\\w+)");
    auto words_begin =
            std::sregex_iterator(s.begin(), s.end(), word_regex);
    auto words_end = std::sregex_iterator();

    std::cout << "Found "
              << std::distance(words_begin, words_end)
              << " words\n";

    const int N = 6;
    std::cout << "Words longer than " << N << " characters:\n";
    for (std::sregex_iterator i = words_begin; i != words_end; ++i) {
        std::smatch match = *i;
        std::string match_str = match.str();
        if (match_str.size() > N) {
            std::cout << "  " << match_str << '\n';
        }
    }

    std::regex long_word_regex("(\\w{7,})");
    std::string new_s = std::regex_replace(s, long_word_regex, "[$&]");
    std::cout << new_s << '\n';

    std::string CMT = "hello world // This is a comment.";
    if (std::regex_search(CMT, CPP_COMMENT)) {
        std::cout << "Text contains Comment!!!\n";

        auto wb = std::sregex_iterator(CMT.begin(), CMT.end(), CPP_COMMENT);
        auto we = std::sregex_iterator();

        std::cout << "Found "  << std::distance(wb, we) << " words\n";

    }

    std::smatch sm;

    //std::regex_search(CMT, sm, CPP_COMMENT);
    //std::cout << "Matchie pos: " << sm.position(0) << '\n';
#endif
    std::map<std::string, int> m{{"CPU", 10}, {"GPU", 15}, {"RAM", 20}};

    Preprocessor p;

    //p._process_file("ASAP2_Demo_V161.a2l");
    p._process_file("comments.txt");

#if 0
    std::string str ("I like to code in C++");
    blank_out(str, 7, 18);
    std::cout << str << '\n';
#endif

    RegExp iii(INCLUDE);
    std::string inci("   /include \"mofakahh.aml\" /* Nize comment */");
    if (iii(inci)) {
        //printf("Include statement found!!! \"%s\"\n", iii.str(1).c_str());
        //printf("Include statement found!!! p:\'%s\' ma:\'%s\' s:\'%s\'\n", iii.prefix().c_str(), iii.str(1).c_str(), iii.suffix().c_str());
        //std::cout << "'" << iii.prefix() << "'" << " '" << iii.str(1) << "'" << " '" << iii.suffix() << "'" << std::endl;
    }

    return 0;
}
