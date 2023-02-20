/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

    (C) 2010-2022 by Christoph Schueler <cpu12.gems.googlemail.com>

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

#include <cstdint>
#include <string>

void escape_string(std::string& line);

class LineMap {
public:
    int lookup(std::uint64_t line_no) const {

    }
private:
};

/*
class PreprocessorResult {

private:
    std::vector<std::string> a2l_data;
    std::vector<std::string> aml_section;
    std::vector<std::string> if_data_sections;
    LineMap line_map;
};

class Preprocessor {
public:

    Preprocessor();

//protected:
    void _process_file(const std::string &filename);
};
*/
