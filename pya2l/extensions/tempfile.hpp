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

#if !defined(__TEMPFILE_HPP)
    #define __TEMPFILE_HPP

    #include <filesystem>
    #include <fstream>
    #include <iostream>

namespace fs = std::filesystem;

/*
 * Create ofstream object and delete on d-tor (or using 'remove()').
 */
class TempFile {
   public:

    explicit TempFile(const std::string& path, bool binary = false) noexcept :
        m_path(fs::path(path)), m_file(path, std::ios::trunc | std::ios::out | (binary ? std::ios::binary : std::ios::out)) {
    }

    TempFile() = delete;

    ~TempFile() noexcept {
        remove();
    }

    std::ofstream& operator()() noexcept {
        return m_file;
    }

    void close() noexcept {
        if (m_file.is_open()) {
            m_file.close();
        }
    }

    std::string abs_path() const noexcept {
        return fs::absolute(m_path.string()).string();
    }

    void remove() noexcept {
        close();
        if (fs::exists(m_path)) {

            // fs::remove(m_path);
        }
    }

    void to_stdout() {
        // m_file.rdbuf(std::cout.rdbuf());
    }

    std::ofstream& handle() noexcept {
        return m_file;
    }

   private:

    fs::path      m_path;
    std::ofstream m_file;
};

#endif  // __TEMPFILE_HPP
