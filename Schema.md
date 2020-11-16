## Tabela Oficinas
* ID: Identificador numérico consecutivo (chave primária);
* Nome: Nome da organização de manutenção;
* Endereço: Endereço da organização de manutenção;
* Complemento: Complemento do endereço da organização de manutenção;
* Cidade: Cidade onde se situa a organização;
* Estado: Estado onde se situa a organização;
* CEP: CEP da rua onde se situa a organização;
* Fone: Telefones para contato com a organização;
* FAX: Telefones com capacidade de receber FAX na organização;
* País: País em que se situa a organização;
* Website: Endereço eletrônico da organização;
* E-mail: Endereço de e-mail para contato com a organização e/ou seus responsáveis;
* Tipo de base: Tipo de base constituída pelas instalações da organização;
* Serviços: Descrição adicional dos serviços prestados pela organização;
* Certificado: Link para o certificado de organização de manutenção emitido pela agência reguladora;
* Especificação Operativa: Link para o documento que descreve as especificações operativas da organização;
* Lista de capacidades: Link para a lista de capacidades da organização, conforme enviado à agência reguladora;
* Status_ID: Status do registro da organização (chave estrangeira) e 
* Última atualização: Data e horário da última atualização.

## Tabela Fabricantes
* ID: Identificador numérico consecutivo (chave primária);
* Nome: Nome da organização fabricante de componentes aeronáuticos.

## Categorias
* ID: Identificador numérico consecutivo (chave primária);
* Categoria/Classe: Nome da categoria e da classe de serviços de manutenção.

## Status
* ID: Identificador numérico consecutivo (chave primária);
* Status: Descrição do status do registro da organização.

## Produtos
* ID: Identificador numérico consecutivo (chave primária);
* Tipo de produto_ID: Identificador do tipo de produto (chave estrangeira);
* Fabricante_ID: Identificador do fabricante (chave estrangeira); e
* Modelo: Modelo da aeronave.

## Tipos_produtos
* ID: Identificador numérico consecutivo (chave primária); e
* Tipo: Descrição do tipo de produto.

## Convalidações
* ID: Identificador numérico consecutivo (chave primária);
* Oficina_ID: Identificador da organização de manutenção (chave estrangeira);
* Autoridade Estrangeira: Nome da autoridade estrangeira;
* Validade: Data de validade da convalidação estrangeira;
* Link: Link para o documento de convalidação estrangeira.

## Oficinas_Produtos
Tabela descreve uma relação de muitos para muitos (many-to-many).
* ID: Identificador numérico consecutivo (chave primária);
* Oficina_ID: Identificador da organização de manutenção (chave estrangeira); e
* Produto_ID: Identificador do produto (chave estrangeira).

## Oficinas_Categorias
Tabela descreve uma relação de muitos para muitos (many-to-many).
* ID: Identificador numérico consecutivo (chave primária);
* Oficina_ID: Identificador da organização de manutenção (chave estrangeira);
* Categoria/Classe_ID: Identificador da Categoria/Classe da organização (chave estrangeira).