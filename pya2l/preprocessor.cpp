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

const std::regex CPP_COMMENT("(?://)(.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_START("(?:/\\*)(.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex MULTILINE_END("(?:\\*/)(.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex INCLUDE("^(?:\\s*)/include\\s+\"([^\"]*)\"", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex AML_START("^\\s*/begin\\s+A[23]ML(.*?)", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex AML_END("^\\s*/end\\s+A[23]ML", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_START("/begin(\\s+)IF_DATA(\\s+)(\\S*)(.*)$", std::regex_constants::ECMAScript | std::regex_constants::optimize);
const std::regex IF_DATA_END("^(.*?)/end(\\s+)IF_DATA(.*)", std::regex_constants::ECMAScript | std::regex_constants::optimize);



// clang++ -Wall -ggdb -std=c++20 preprocessor.cpp -o preprocessor.exe


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

    auto FN{ "C:\\csProjects\\pyA2L\\pya2l\\examples\\03G906021KE_9970_501409_P447_HAXN_EDC16U34_3.41.a2l" };

    Preprocessor p;

    if (argc > 1) {
        p.process(argv[1]);
        //auto res = ifdata_reader.get({ 2179, 4, 2184, 16 });
        //res = ifdata_reader.get({ 1051, 8, 1056, 20 });
    } else {
        //p._process_file("ASAP2_Demo_V161.a2l");
        p.process("comments.txt");

        ld(p, 1);
        ld(p, 3);
        ld(p, 4);
        ld(p, 8);
        ld(p, 12);
        ld(p, 13);

        //ld(p, 1079);
        //ld(p,1080);
        //ld(p,1081);
        //ld(p,1095);
        //ld(p,10900);


    }
    return 0;
}
