
#include <stack>

#include "a2llg.h"
#include "antlr4-runtime.h"
#include "ifdata.hpp"
#include "unmarshal.hpp"
#include "logger.hpp"

using namespace antlr4;

Node unmarshal(const std::stringstream& data);
	

Node load_grammar(const std::string& file_name) {
    std::ifstream aml_stream;
    aml_stream.open(file_name, std::ios_base::binary);
    std::stringstream aml_buffer;
    aml_buffer << aml_stream.rdbuf();
    return unmarshal(aml_buffer);
}

class IfDataParser {
   public:

    using token_t = std::optional<std::tuple<int, std::string>>;

    IfDataParser() = delete;

    explicit IfDataParser(const Node& root, const std::string& ifdata_section) : m_ifdata_section(ifdata_section), m_root(root) {
        m_grammar.push(&m_root);
        m_input = ANTLRInputStream(m_ifdata_section);
        m_lexer = std::make_unique<a2llg>(&m_input);
        //logger.setName("pya2l.IfDataParser");
        // logger.setLevel(LogLevel::DEBUG);
        consume();
    }

    void parse() {
        const auto root = get_root();
        if (root) {
            m_grammar.push(root);
            consume();
            do_type();
        }
    }

    const Node * get_root() {
        auto token = current_token();
        const auto [type, text] = *token;
        consume();
        const auto [type2, text2] = *current_token();

        if (type == a2llg::BEGIN) {
            if ((type2 == a2llg::IDENT) && (text2 == "IF_DATA")) {
                for (const auto& member: top()->map().at("MEMBERS").list()) {
                    const auto& mmap = member.map();

                    if (member.aml_type() == Node::AmlType::BLOCK) {
                        const auto tag = std::get<std::string>(mmap.at("TAG").value());
                        if (tag == "IF_DATA") {
                            return &member;
                        }
                    }
                    else {
                        const auto name = std::get<std::string>(mmap.at("NAME").value());
                        std::cout << "Name: " << name << std::endl;
                        if (name == "if_data") {
                            return &member;
                        }
                    }


                }
            }
        }

        return nullptr;
    }

    token_t next_token() {
        auto tok        = m_lexer->nextToken();
        auto token_type = tok->getType();
        if (token_type == antlr4::Lexer::EOF) {
            return std::nullopt;
        }
        return std::make_tuple<int, std::string>(token_type, tok->getText());
    }

    token_t current_token() {
        return m_current_token;
    }

    void consume() {
        m_current_token = next_token();
    }

    const Node* top() const noexcept {
        if (m_grammar.empty()) {
			spdlog::error("Stack is empty");
        }
        return m_grammar.top();
    }

    void block_type() {
        auto token = current_token();
        if (token) {
            auto [type, text] = *token;
            if (type == a2llg::IDENT) {
                const Node* blk = top()->find_block(text);
                if (blk) {
                    m_grammar.push(blk);
                }
                consume();
                const auto& [multiple, member, type] = blk->member_or_type();
                const auto& map                      = top()->map();
                auto        tk                       = current_token();
                if (type) {
                    m_grammar.push(*type);
                    switch ((*type)->aml_type()) {
                        case Node::AmlType::STRUCT:
                            struct_type();
                            break;
                        case Node::AmlType::TAGGED_STRUCT:
                            tagged_struct_type();
                            break;
                        case Node::AmlType::TAGGED_UNION:
                            tagged_union_type();
                            break;
                        case Node::AmlType::ENUMERATION:
                            enumeration_type();
                            break;
                        case Node::AmlType::PDT:
                            pdt_type();
                            break;
                        default:
                            std::cerr << "[ERROR (pya2l.IF_DATAParser)] " << "Unknown type: " << std::endl;
                            // m_loogger.error("Unknown type: ", static_cast<int>((*type)->aml_type()));
                            break;
                    }
                } else if (member) {
                    const auto mem_real = *member;
                    if (mem_real->aml_type() == Node::AmlType::TAGGED_STRUCT_MEMBER) {
                        const auto& def                         = mem_real->map().at("DEFINITION");
                        const auto& [mmultiple, mmember, mtype] = def.member_or_type();
                        m_grammar.push(*mtype);
                        do_type();
                        m_grammar.pop();
                    }
                    // m_grammar.push(*member);
                }
                m_grammar.pop();
            }
        }
    }

    bool match(int token_type, const std::optional<std::string>& value = std::nullopt) {
#if 0
        def match(self, token_type, value = None) :
            ok = self.current_token.type == token_type
            token_value = self.value(self.current_token)
            self.consume()
            if value is None :
        return ok
            else:
        if not ok :
            return False
            return token_value == value
#endif
    }

    void struct_type() {
        const auto tos = top();
        for (const auto& member : tos->get_members()) {
            auto token = current_token();
            if (token) {
                auto [tp, text] = *token;
            }
            consume();
        }
    }

    void tagged_struct_type() {
        auto token = current_token();
        if (token) {
            auto [tp, text]              = *token;
            const auto  tos              = top();
            const auto& ts_members       = tos->get_tagged_struct_members();
            const auto& [member, b0, b1] = ts_members.at(text);
            const auto& [arr_spec, type] = member->get_type();
            m_grammar.push(type);
            consume();
            do_type();
            m_grammar.pop();
        }
    }

    void tagged_union_type() {
        auto token = current_token();
        if (token) {
            auto [tp, text]              = *token;
            const auto  tu_member        = top()->find_tag(text);
            const auto& member           = tu_member->map().at("MEMBER");
            const auto& [arr_spec, type] = member.get_type();
            m_grammar.push(type);
            consume();
            do_type();
            m_grammar.pop();
        }
    }

    void do_type() {
        const auto tos   = top();
        auto       token = current_token();
        if (token) {
            auto [type, text] = *token;
            switch (type) {
                case a2llg::BEGIN:
                    consume();
                    block_type();
                    break;
                default:
                    spdlog::error("Unknown token type: {}", type);
            }
        }

        switch (tos->aml_type()) {
            case Node::AmlType::STRUCT:
                struct_type();
                break;
            case Node::AmlType::TAGGED_STRUCT:
                tagged_struct_type();
                break;
            case Node::AmlType::TAGGED_UNION:
                tagged_union_type();
                break;
            case Node::AmlType::ENUMERATION:
                enumeration_type();
                break;
            case Node::AmlType::PDT:
                pdt_type();
                break;
            case Node::AmlType::BLOCK:
                block_type();
                break;
            default:
                spdlog::error("Unknown AmlType: ");
                break;
        }
    }

    void enumeration_type() {
    }

    void pdt_type() {
    }

   private:

    const std::string       m_ifdata_section;
    ANTLRInputStream        m_input;
    const Node&             m_root;
    std::stack<const Node*> m_grammar{};
    std::unique_ptr<a2llg>  m_lexer;
    token_t                 m_current_token;
};

const std::string BASE{ "C:/csProjects/" };
//const std::string BASE{ "C:/Users/HP/PycharmProjects/" };

const std::string CPLX_TEXT{ ""
                             "  /begin IF_DATA ASAP1B_CCP"
                             "      /begin SOURCE"
                             "	      \"segment synchronous event channel\""
                             "		  103"
                             "		  1"
                             "		  /begin QP_BLOB"
                             "		      0"
                             "			  LENGTH 8"
                             "			  CAN_ID_FIXED 0x330"
                             "			  FIRST_PID 0"
                             "			  RASTER 0"
                             "		  /end QP_BLOB"
                             "	  /end SOURCE"
                             "  "
                             "      /begin SOURCE"
                             "	      \"10ms time synchronous event channel\""
                             "		  4"
                             "		  1"
                             "		  /begin QP_BLOB"
                             "		      1"
                             "			  LENGTH 12"
                             "			  CAN_ID_FIXED 0x340"
                             "			  FIRST_PID 8"
                             "			  RASTER 1"
                             "		  /end QP_BLOB"
                             "	  /end SOURCE"
                             "  "
                             "      /begin SOURCE"
                             "	      \"100ms time synchronous event channel\""
                             "		  4"
                             "		  10"
                             "		  /begin QP_BLOB"
                             "		      2"
                             "			  LENGTH 8"
                             "			  CAN_ID_FIXED 0x350"
                             "			  FIRST_PID 20"
                             "			  RASTER 2"
                             "		  /end QP_BLOB"
                             "	  /end SOURCE"
                             "  "
                             "      /begin RASTER"
                             "	      \"segment synchronous event channel\""
                             "	      \"seg_sync\""
                             "		  0"
                             "		  103"
                             "		  1"
                             "	  /end RASTER"
                             "  "
                             "      /begin RASTER"
                             "	      \"10ms time synchronous event channel\""
                             "	      \"10_ms\""
                             "		  1"
                             "		  4"
                             "		  1"
                             "	  /end RASTER"
                             "  "
                             "      /begin RASTER"
                             "	      \"100ms time synchronous event channel\""
                             "	      \"100_ms\""
                             "		  2"
                             "		  4"
                             "		  10"
                             "	  /end RASTER"
                             "  "
                             "	  /begin SEED_KEY"
                             "	       \"\""
                             "	       \"\""
                             "	       \"\""
                             "	  /end SEED_KEY"
                             "  "
                             "	  /begin TP_BLOB"
                             "	       0x200"
                             "		   0x202"
                             "		   0x200"
                             "		   0x210"
                             "		   0x1234"
                             "		   1"
                             "          "
                             "		  /begin CAN_PARAM"
                             "		       0x3E8"
                             "			   0x40"
                             "			   0x16"
                             "		  /end CAN_PARAM"
                             "          "
                             "		  DAQ_MODE    BURST"
                             "		  CONSISTENCY DAQ"
                             "          "
                             "		  /begin CHECKSUM_PARAM "
                             "		       0xC001"
                             "		       0xFFFFFFFF"
                             "		      CHECKSUM_CALCULATION ACTIVE_PAGE"
                             "          /end CHECKSUM_PARAM "
                             "          "
                             "		  /begin DEFINED_PAGES"
                             "		      1"
                             "			  \"reference page\""
                             "			   0x00"
                             "			   0x8E0670"
                             "			   0x1C26C"
                             "			  ROM"
                             "		  /end DEFINED_PAGES"
                             "          "
                             "		  /begin DEFINED_PAGES"
                             "		      2"
                             "			  \"working page\""
                             "			   0x00"
                             "			   0x808E0670"
                             "			   0x1C26C"
                             "			  RAM"
                             "			  RAM_INIT_BY_ECU"
                             "		  /end DEFINED_PAGES"
                             "          "
                             "		  OPTIONAL_CMD 0x11  "
                             "		  OPTIONAL_CMD 0xE  "
                             "		  OPTIONAL_CMD 0x19  "
                             "		  OPTIONAL_CMD 0x9  "
                             "		  OPTIONAL_CMD 0xC  "
                             "		  OPTIONAL_CMD 0xD  "
                             "		  OPTIONAL_CMD 0x12  "
                             "		  OPTIONAL_CMD 0x13  "
                             "	  /end TP_BLOB"
                             "  /end IF_DATA" };

const std::string CPLX_TEXT2{
"  /begin IF_DATA ASAP1B_KWP2000 " \
"      /begin SOURCE " \
"	      \"timeslot\" " \
"		  0 " \
"		  0 " \
"		  QP_BLOB " \
"		      0 " \
"			  BLOCKMODE " \
"			  0xF0 " \
"			  0 " \
"              20 " \
"	  /end SOURCE " \
"  " \
"	  /begin TP_BLOB " \
"		  0x100 " \
"		  0x11 " \
"		  0xF1 " \
"		  WuP " \
"		  MSB_LAST " \
"          1 " \
"          0x00000 " \
"          " \
"		  SERAM " \
"		      0x10000 " \
"		      0x10000 " \
"		      0x13FFF " \
"		      0x17FFF " \
"			  0x000000 " \
"			  0x000000 " \
"              1 " \
"              1 " \
"              1 " \
"              1 " \
"          " \
"		  /begin CHECKSUM " \
"              0x010201 " \
"              1 " \
"              1 " \
"              RequestRoutineResults " \
"              RNC_RESULT 0x23 " \
"          /end CHECKSUM " \
"          " \
"          /begin FLASH_COPY " \
"              TOOLFLASHBACK " \
"              3 " \
"              RequestRoutineResults " \
"              RAM_InitByECU " \
"              0x86 " \
"              COPY_FRAME 1 " \
"              RNC_RESULT 0x23 0xFB 0xFC " \
"              COPY_PARA 1 " \
"          /end FLASH_COPY " \
"          " \
"          BAUD_DEF " \
"              105600 " \
"              0x86 " \
"              0x81 " \
"          BAUD_DEF " \
"              211200 " \
"              0x86 " \
"              0xA1 " \
"          BAUD_DEF " \
"              156250 " \
"              0x86 " \
"              0x91 " \
"          BAUD_DEF " \
"              125000 " \
"              0x86 " \
"              0x87 " \
"          BAUD_DEF " \
"              10400 " \
"              0x86 " \
"              0x14 " \
"          " \
"          TIME_DEF " \
"              0x0001 " \
"              0x0000 " \
"              0x0032 " \
"              0x0003 " \
"              0x0200 " \
"              0x0000 " \
"          TIME_DEF " \
"              0x0001 " \
"              0x0000 " \
"              0x0032 " \
"              0x0003 " \
"              0x0200 " \
"              0x0001 " \
"          " \
"          SECURITY_ACCESS " \
"              1 " \
"              1 " \
"              0 " \
"          " \
"	  /end TP_BLOB " \
"  /end IF_DATA "};

#if 0
int main() {

    std::ifstream stream;

    stream.open(BASE + "pyA2L/pya2l/examples/some_if_data.txt");

    ANTLRInputStream input(stream);

    auto ifd_lexer = a2llg(&input);


    auto root = load_grammar(BASE + "pyA2L/pya2l/examples/aml_dump.bin");

    std::string TEXT("/begin IF_DATA ETK\n"
                     "ADDRESS_MAPPING\n"
                     "0x10000\n"
                     "0x10000\n"
                     "0x1E8\n"
                     "/end IF_DATA");
    // auto        lex = IfDataParser(root, TEXT);
    auto lex = IfDataParser(root, CPLX_TEXT2);

    lex.parse();

    return 0;
}

#endif

int main() {
    return 0;
}
