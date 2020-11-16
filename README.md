# Oficinas Request

Módulo python criado para a captura e armazenamento de informações de organizações de manutenção aeronáutica,
contento as funções:
* download_providers_info para download de informações;
* parse_providers_info para análise das informações baixadas; e
* providers_info_to_excel para exportar os dados para uma planilha.

Quando executado de forma direta, o módulo baixa, analisa e exporta as informações dos prestadores de serviços 
de manutenção aeronáuticas para uma planilha do Excel.

## Funções
### download_providers_info
Não aceita argumentos, baixa os índices de oficinas e, após, captura informações de cada uma individualmente.

### parse_providers_info
Não aceita argumentos, analisa todas as informações capturadas pela função **download_providers_info**.  
Retorna uma lista contendo dicionários com as informações obtidas a partir dos dados capturados.

Os dicionários criados contêm as chaves:  
* 'Nome' : Nome da organização de manutenção;
* 'Endereço': Endereço da organização;
* 'Complemento': Complemento do endereço da organização;
* 'Cidade': Cidade onde se situa a organização;
* 'Estado': Estado onde se situa a organização;
* 'CEP': CEP da rua onde se situa a organização;
* 'Fone': Telefones da organização de manutenção;
* 'FAX': Número de telefone com capacidade de receber FAX;
* 'País': País onde se situa a organização;
* 'Website': Endereço eletrônico do site da organização;
* 'Email': E-mails para contato com a organização;
* 'Tipo de base': Tipo de base da organização;
* 'Categorias/Classes': Lista de categorias e classes em que a empresa está habilitada a atuar;
* 'Status': Status da organização de manutenção junto à ANAC;
* 'Serviços': Informação adicional dos serviços prestados pela instituição;
* 'Certificado': URL para o certificado de organização de manutenção, emitido pela ANAC
* 'Espec. Operativa': URL para as especificações operativas da organização;
* 'Lista de Capac.': URL para a lista de capacidades da organização;
* 'Convalidações estrangeiras': Lista contendo dicionários de convalidações estrangeiras, com agência, data de validade
 e URL para o documento.
* 'Produtos': Lista contendo dicionários de produtos, classificados por tipo de produto e fabricante;

### providers_info_to_excel
Toma o dicionário gerado pela função **parse_providers_info** como argumento, não retorna nada.
Cria uma planilha do excel contendo os dados das organizações de manutenção, onde cada planilha corresponde a uma tabela
em um banco de dados.