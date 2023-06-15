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

#include "preprocessor.hpp"

// clang++ -Wall -ggdb -std=c++20 preprocessor.cpp -o preprocessor.exe


void ld(Preprocessor& p, std::size_t line_no)
{
    auto res = p.line_map.lookup(line_no);
    if (res.has_value()) {
        auto [name, num] = res.value();
        std::cout << "\t\t" << line_no << " ==> [" << name << "] " << num << std::endl;
    } else {
        std::cout << line_no << " not found!" << std::endl;
    }
}

void test_strings()
{
    std::string line;
    std::ifstream file("strings.txt");

    auto idx{ 0 };
    if (file.is_open()) {
        while (!file.eof()) {
            std::getline(file, line);
            escape_string(line);
            std::cout << line << std::endl;
            idx++;
        }
    }
    std::exit(1);
}

#include "extensions/tokenizer.hpp"

int main(int argc, char** argv)
{
    bool cmd = false;
    auto FN{ "C:\\csProjects\\pyA2L\\examples\\03G906021KE_9970_501409_P447_HAXN_EDC16U34_3.41.a2l" };

    cmd = argc > 1;

    Preprocessor p{"INFO"};

    if (cmd) {
        p.process(argv[1], "UTF-8");
    } else {
        p.process("comments.txt", "UTF-8");

        ld(p, 1);
        ld(p, 3);
        ld(p, 4);
        ld(p, 8);
        ld(p, 11);
        ld(p, 18);
    }
    return 0;
}
