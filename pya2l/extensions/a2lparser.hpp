
#if !defined(__A2LPARSER_HPP)
    #define __A2LPARSER_HPP

    #include <algorithm>
    #include <array>
    #include <cstdint>
    #include <cstdlib>
    #include <fstream>
    #include <iostream>
    #include <limits>
    #include <map>
    #include <set>
    #include <sstream>
    #include <stack>
    #include <unordered_map>
    #include <unordered_set>
    #include <variant>
    #include <vector>

using AsamVariantType = std::variant<std::string, unsigned long long, signed long long, long double>;

    #include "a2ltoken.hpp"
    #include "asam_types.hpp"
    #include "keyword.hpp"
    #include "parameter.hpp"
    #include "parser_table.hpp"
    #include "preprocessor.hpp"
    #include "token_stream.hpp"
    #include "valuecontainer.hpp"


class AsapVersion {
public:
    // Default constructor
    AsapVersion() noexcept : m_major(0), m_minor(0), m_valid(false) {}

    // Constructor with parameters
    AsapVersion(unsigned long long major, unsigned long long minor) noexcept
        : m_major(major), m_minor(minor), m_valid(major > 0) {}

    // Copy constructor
    AsapVersion(const AsapVersion& other) noexcept = default;

    // Move constructor
    AsapVersion(AsapVersion&& other) noexcept = default;

    // Copy assignment operator
    AsapVersion& operator=(const AsapVersion& other) noexcept = default;

    // Move assignment operator
    AsapVersion& operator=(AsapVersion&& other) noexcept {
        if (this != &other) {
            m_major = other.m_major;
            m_minor = other.m_minor;
            m_valid = other.m_major > 0;
        }
        return *this;
    }

    // Accessors
    bool is_valid() const noexcept {
        return m_valid;
    }

    unsigned long long major() const noexcept {
        return m_major;
    }

    unsigned long long minor() const noexcept {
        return m_minor;
    }

private:
    unsigned long long m_major;
    unsigned long long m_minor;
    bool m_valid;

};

class A2LParser {
   public:

    using value_table_t = std::tuple<std::string, std::string, std::vector<std::vector<AsamVariantType>>>;

    explicit A2LParser(
        std::optional<preprocessor_result_t> prepro_result, const std::string& file_name, const std::string& encoding,
        spdlog::level::level_enum log_level
    ) :
        m_prepro_result(std::move(prepro_result)),
        m_keyword_counter(0),
        m_table(PARSER_TABLE),
        m_root("root"),
        m_finalized(false),
        m_table_count(0) {

        kw_push(m_table);
        m_value_stack.push(&m_root);

        if (m_prepro_result) {
            m_idr = std::make_unique<IfDataReader>(std::get<2>(m_prepro_result.value()));
            m_idr->open();
        }

        m_logger = create_logger("a2lparser", log_level);
        parse(file_name, encoding);
        // Don't call spdlog::shutdown() here as it affects all loggers globally
    }

    // Delete copy constructor
    A2LParser(const A2LParser&) = delete;

    // Delete copy assignment operator
    A2LParser& operator=(const A2LParser&) = delete;

    // Move constructor
    A2LParser(A2LParser&& other) noexcept
        : m_prepro_result(std::move(other.m_prepro_result)),
          m_logger(std::move(other.m_logger)),
          m_idr(std::move(other.m_idr)),
          m_encoding(std::move(other.m_encoding)),
          m_reader(std::move(other.m_reader)),
          m_keyword_counter(other.m_keyword_counter),
          m_kw_stack(std::move(other.m_kw_stack)),
          m_value_stack(std::move(other.m_value_stack)),
          m_table(other.m_table),
          m_root(std::move(other.m_root)),
          m_tables(std::move(other.m_tables)),
          m_table_count(other.m_table_count),
          m_finalized(other.m_finalized),
          m_asam_version(std::move(other.m_asam_version)) {

        // Mark the moved-from object as finalized to prevent double-close
        other.m_finalized = true;
    }

    // Move assignment operator
    A2LParser& operator=(A2LParser&& other) noexcept {
        if (this != &other) {
            // Close current resources
            close();

            // Move resources from other
            m_prepro_result = std::move(other.m_prepro_result);
            m_logger = std::move(other.m_logger);
            m_idr = std::move(other.m_idr);
            m_encoding = std::move(other.m_encoding);
            m_reader = std::move(other.m_reader);
            m_keyword_counter = other.m_keyword_counter;
            m_kw_stack = std::move(other.m_kw_stack);
            m_value_stack = std::move(other.m_value_stack);
            // m_table is a reference and can't be reseated
            m_root = std::move(other.m_root);
            m_tables = std::move(other.m_tables);
            m_table_count = other.m_table_count;
            m_finalized = other.m_finalized;
            m_asam_version = std::move(other.m_asam_version);

            // Mark the moved-from object as finalized to prevent double-close
            other.m_finalized = true;
        }
        return *this;
    }

    ~A2LParser() {
        close();
    }

    void close() noexcept {
        if (!m_finalized) {
            try {
                if (m_reader) {
                    m_reader->close();
                }

                if (m_prepro_result && m_idr) {
                    m_idr->close();
                }
            } catch (...) {
                // Suppress any exceptions during cleanup
                // Log error if logger is available
                if (m_logger) {
                    m_logger->error("Exception during close operation");
                }
            }

            m_finalized = true;
        }
    }

    void parse(const std::string& file_name, const std::string& encoding) {
        ValueContainer::set_encoding(encoding);
        std::optional<std::string> if_data_section;
        m_reader = std::make_unique<TokenReader>(file_name);

        while (true) {
            const auto token = m_reader->LT(1);
            if_data_section  = std::nullopt;

            if (token_type() == A2LTokenType::BEGIN) {
                m_reader->consume();
            }

            // Handle END token
            if (token_type() == A2LTokenType::END) {
                handle_end_token();
                continue;
            }

            if (token->getType() == ANTLRToken::_EOF) {
                if (std::size(m_kw_stack) > 1) {
                    m_logger->error("Premature end of file!!!");
                }
                break;
            }

            if (kw_tos().contains(token->getType())) {
                const auto ttype = kw_tos().get(token->type());
                kw_push(ttype);
                auto& vref = value_tos().add_keyword(ValueContainer(ttype.m_class_name));
                m_value_stack.push(&vref);
            } else {

                // TODO: Addressmapper
                auto kwt = kw_tos();
                m_logger->error("Invalid token : {}", token->toString());
                if ((token->getText() == "IF_DATA") && (kwt.m_name == "ROOT")) {
                    m_logger->error("No top-level PROJECT element. This is probably an include file?");
                }
                break;
            }

            if (token->getText() == "IF_DATA") {
                if (m_prepro_result) {
                    if_data_section = m_idr->get({ token->getLine(), token->column() + 1 });
                }
            }
            m_reader->consume();
            m_keyword_counter++;
            auto kw = ValueContainer(kw_tos().m_name);

            if (kw.get_name() == "VAR_FORBIDDEN_COMB") {
                auto fc = true;
            }
            auto [p, m] = do_parameters();
            value_tos().set_parameters(std::move(p));
            value_tos().set_multiple_values(std::move(m));
            if (if_data_section) {
                value_tos().add_if_data(if_data_section.value());
                if_data_section = std::nullopt;
            }
            if (value_tos().get_name() == "Asap2Version") {
                const auto& version_par_vec = value_tos().get_parameters();
                if (std::size(version_par_vec) == 2) {
                    auto major_v = version_par_vec[0];
                    auto minor_v = version_par_vec[1];
                    m_asam_version = AsapVersion(variant_get<unsigned long long>(major_v), variant_get<unsigned long long>(minor_v));
                }
                if (m_asam_version.is_valid() && (m_asam_version.major() == 1)) {
                    if (m_asam_version.minor() <= 5) {
                        m_logger->warn("ASAP version {}.{} may only parsed with errors.", m_asam_version.major(), m_asam_version.minor());
                    }
                }
            }
            if (kw_tos().m_block == false) {
                kw_pop();
                m_value_stack.pop();
            }
            if (token_type() == A2LTokenType::END) {
                handle_end_token();
            }
        }
    }

    const std::vector<value_table_t>& get_tables() const noexcept {
        return m_tables;
    }

    const ValueContainer& get_values() const noexcept {
        return m_root;
    }

    std::size_t get_keyword_counter() const noexcept {
        return m_keyword_counter;
    }

   protected:

    auto do_parameters() -> std::tuple<ValueContainer::key_value_list_t, std::vector<AsamVariantType>>

    {
        auto                         done           = false;
        auto                         parameter_list = ValueContainer::key_value_list_t{};
        std::vector<AsamVariantType> m_multiple_values;
        auto                         param_count = 0;

        for (const auto& parameter : kw_tos().m_parameters) {
            done = !parameter.is_multiple();
            do {
                auto token = m_reader->LT(1);

                if ((kw_tos().contains(token->getType())) || (kw_tos(1).contains(token->getType())) ||
                    (token_type() == A2LTokenType::BEGIN) ||
                    ((token_type() == A2LTokenType::END) && (parameter.is_multiple() == false))) {
                    // Not all parameters are present.

					if (!((std::size(parameter_list) == (std::size(kw_tos().m_parameters) - 1)) && parameter.is_multiple())) {
						m_logger->warn("{} is missing one or more required parameters: ", kw_tos().m_name);

                        for (std::size_t idx = param_count; idx < std::size(kw_tos().m_parameters); ++idx) {
                            auto p = kw_tos().m_parameters[idx];
                            m_logger->warn("\t{}", p.get_name());
                            switch (p.get_type()) {
                                case PredefinedType::Int:
                                case PredefinedType::Uint:
                                case PredefinedType::Long:
                                case PredefinedType::Ulong:
                                    parameter_list.push_back(0);
                                    break;

                                case PredefinedType::Float:
                                    parameter_list.push_back(0.0);
                                    break;

                                default:
                                    parameter_list.push_back("");
                                    break;
                            }
                        }
                    }
                    return { parameter_list, m_multiple_values };

                }
                param_count++;

                if (parameter.is_tuple()) {
                    auto tuple_parser = ParameterTupleParser(parameter);
                    if (parameter.tuple_has_counter()) {
                        tuple_parser.feed(token);
                        m_reader->consume();
                    }
                    while (true) {
                        token = m_reader->LT(1);
                        tuple_parser.feed(token);
                        if (tuple_parser.get_state() == ParameterTupleParser::StateType::FINISHED) {
                            if (!std::holds_alternative<std::string>(parameter_list[0])) {
                                m_logger->error("Invalid tuple.");
                                break;
                            }
                            m_tables.push_back({ value_tos().get_name(), std::get<std::string>(parameter_list[0]),
                                                 tuple_parser.get_table() });
                            m_reader->consume();
                            break;
                        }
                        auto next_token = m_reader->LT(2);
                        if (static_cast<A2LTokenType>(next_token->getType()) == A2LTokenType::END) {
                            m_tables.push_back({ value_tos().get_name(), "", tuple_parser.get_table() });
                            tuple_parser.finished();
                            m_reader->consume();
                            break;
                        }
                        m_reader->consume();
                    }
                } else {
                    if ((parameter.is_multiple() == true) && (token_type() == A2LTokenType::END)) {
                        done = true;
                        continue;
                    }

                    std::string token_text = token->getText();
                    const auto param_type = parameter.get_type();
                    using enum PredefinedType;

                    // Handle sign for numeric types
                    if (((param_type == Int) || (param_type == Uint) || (param_type == Long) || (param_type == Ulong) ||
                         (param_type == Float)) &&
                        ((token_text == "-") || ((token_text == "+")))) {
                        m_reader->consume();
                        // Reserve space for the concatenated string to avoid reallocation
                        token_text.reserve(token_text.size() + m_reader->LT(1)->getText().size());
                        token_text += m_reader->LT(1)->getText();
                    }

                    const auto value = convert(param_type, token_text);

                    const auto valid = validate(parameter, token, value);
                    if (!valid) {
                       m_logger->error("Invalid param: {} token: {}", parameter.get_name(), token->toString());
                    }

                    if (parameter.is_multiple() == true) {
                        m_multiple_values.emplace_back(value);
                    } else {
                        parameter_list.emplace_back(value);
                    }
                    m_reader->consume();
                }
            } while (!done);
        }
        return { parameter_list, m_multiple_values };
    }

    Keyword& kw_tos(std::size_t pos = 0) {
        const auto offset = std::size(m_kw_stack) - pos - 1;
        return m_kw_stack[offset];
    }

    const Keyword& kw_tos(std::size_t pos = 0) const {
        const auto offset = std::size(m_kw_stack) - pos - 1;
        return m_kw_stack[offset];
    }

    void kw_push(const Keyword& kw) {
        m_kw_stack.push_back(kw);
    }

    void kw_pop() {
        m_kw_stack.pop_back();
    }

    ValueContainer& value_tos() {
        return *m_value_stack.top();
    }

    const ValueContainer& value_tos() const {
        return *m_value_stack.top();
    }

    A2LTokenType token_type(int k = 1) const {
        return static_cast<A2LTokenType>(m_reader->LT(k)->getType());
    }

    // Handle END token processing
    void handle_end_token() {
        m_reader->consume();
        const auto glied = m_reader->LT(1);

        // Verify that the END token matches the current keyword
        if (kw_tos().m_name != glied->getText()) {
            m_logger->error("END token mismatch: expected '{}', got '{}'",
                           kw_tos().m_name, glied->getText());
        } else {
            kw_pop();
            m_value_stack.pop();
        }

        m_reader->consume();
    }

   private:

    std::optional<preprocessor_result_t> m_prepro_result;
	std::shared_ptr<spdlog::logger>      m_logger;
    std::unique_ptr<IfDataReader>        m_idr;
    std::string                          m_encoding;
    std::unique_ptr<TokenReader>         m_reader;
    std::size_t                          m_keyword_counter;
    std::vector<Keyword>                 m_kw_stack;
    std::stack<ValueContainer*>          m_value_stack;
    Keyword&                             m_table;
    ValueContainer                       m_root;
    std::vector<value_table_t>           m_tables;
    std::size_t                          m_table_count{ 0 };
    bool                                 m_finalized{ false };
    AsapVersion                          m_asam_version;
};

#endif  // __A2LPARSER_HPP
