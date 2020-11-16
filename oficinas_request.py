import xlsxwriter
import shutil
import requests
import datetime
import os
import re
from bs4 import BeautifulSoup


def timestamp():
    """
    Takes no arguments.
    Returns a timestamp tag to put before status for printing and logging purposes.
    :return: string
    """
    return f"[{datetime.datetime.now().strftime('%H:%M:%S')}]"


def download_providers_info():
    """
    Takes no arguments.
    Downloads the index of maintenance service providers from the Brazilian aviation authority (ANAC), then itterates
    over it, download the individual htmls containing the publicly available information about each of the said
    maintenance service providers.
    :return: None
    """
    # Index download
    r = requests.Session()

    process_status = f'\n{timestamp()} Download indexes'
    print(process_status, end='')

    index_content = r.get('https://sistemas.anac.gov.br/certificacao/AvGeral/AIR145BasesPadrao.asp?')
    bs = BeautifulSoup(index_content.text, 'html.parser')

    links = {a.text.strip('\n '): "https://sistemas.anac.gov.br/certificacao/AvGeral/" + a['href']
             for a in bs.select('td[bgcolor] > a')}

    print(' - \033[92mDone\033[0m')

    addresses = {}

    # Index parsing
    print(f'{timestamp()} Get maintenance service providers links from indexes')
    for sector in links.keys():
        print(f'    Get links for class "{sector}"', end='')
        content = r.get(links[sector])
        soup = BeautifulSoup(content.text, 'html.parser')
        t = soup.find('table', {'id': 'TableId'})

        # Retrieves providers from the index table
        service_providers = t.select('tr[onmouseover]')

        # Creates a dictionary with providers' names and urls to the respectives informations pages
        for tag in service_providers:
            if tag.text.strip() not in addresses.keys():
                addresses[tag.text.strip()] = 'https://sistemas.anac.gov.br/certificacao/AvGeral/' + \
                                               tag.find('a')['href']

        print(f' - \033[92mDone\033[0m ({len(service_providers)} maintenance service providers located)')
    print(f'    \033[96mGet maintenance service providers links from indexes\033[0m '
          f'- \033[92mDone \033[0m({len(addresses)} maintenance service providers located)\n')

    print(f'{timestamp()} Clean folder and create backup', end='')

    # Create the default download directory if it not yet exists
    if not os.path.isdir('html_empresas'):
        os.mkdir('html_empresas')
        os.mkdir('html_empresas\\previous')
    elif not os.path.isdir('html_empresas\\previous'):
        os.mkdir('html_empresas\\previous')

    this_folder_path = os.path.abspath('html_empresas')
    new_folder_path = os.path.abspath('html_empresas\\previous')

    # Clean the download directory, to ensure no service provider information is parsed more than once
    if len(os.listdir(new_folder_path)) > 0:
        for file in os.listdir(new_folder_path):
            os.remove(os.path.join(new_folder_path, file))

    if len(os.listdir(this_folder_path)) > 0:
        for file in os.listdir('html_empresas'):
            if file[-5:].lower() == '.html':
                os.rename(os.path.join(this_folder_path, file), os.path.join(new_folder_path, file))

    print(" - \033[92mDone\033[0m")

    # Download HTMLs containing maintenance service providers information
    status = f'{timestamp()} Downloading maintenance service providers info - '
    print(status, end='')
    n = 1
    for empresa in addresses:
        s = f'{n}/{len(addresses)} ({round(n/len(addresses)*100, 2)}%): {empresa}'
        print(s, end='')
        # Write information to HTML files in the default download directory
        while True:
            with open(f'html_empresas\\{empresa.replace("/", "")}.html', 'w', encoding='utf-8') as fileHandle:
                fileHandle.write(BeautifulSoup(r.get(addresses[empresa]).content.decode('latin-1', 'ignore'),
                                               'html.parser').prettify())

            if len(open(f'html_empresas\\{empresa.replace("/", "")}.html', 'r', encoding='utf-8').readlines()) > 0:
                break

        n += 1
        print('\b'*(len(s)), end='')
    print('\b'*(len(status)), end='')

    print(f"{timestamp()} Download of maintenance service providers info - \033[92mDone\033[0m "
          f"({len(os.listdir('html_empresas'))-1} files downloaded)")

    return None


def parse_providers_info():
    """
    Takes no arguments.
    Parses the information inside the HTMLs in the default download folder.

    Retrieved information includes:
        Name,
        Address,
        Address complement,
        City,
        State,
        Telephone,
        Country,
        Website,
        E-mail,
        Base type,
        Categories/Classes,
        Status, Certificate,
        Operative Specifications,
        Capabilities List,
        Foreign Co-validation, and
        products.

    :return: list of dictionaries containing maintenance service providers information
    """
    s = ''

    # Dictionary of months as used in the information pages
    mdict = {'jan.': 1,
             'fev.': 2,
             'mar.': 3,
             'abr.': 4,
             'mai.': 5,
             'jun.': 6,
             'jul.': 7,
             'ago.': 8,
             'set.': 9,
             'out.': 10,
             'nov.': 11,
             'dez.': 12,
             }

    # Compile lists of available HTML files in default download directory
    empresas_file_list = os.listdir('html_empresas')
    emp_info_list = []
    print(f'{timestamp()} Service provider info parsing - ', end='')
    n = 1

    # Iterates over the list of available HTMLs
    for file in empresas_file_list:
        try:
            s = f'({n}/{len(empresas_file_list)} - {round(n/len(empresas_file_list)*100, 2)}%) - {file}'
            print(s, end='')
            # Read HTML file
            with open(f'html_empresas\\{file}', 'r', encoding='utf-8') as fileHandle:
                html = BeautifulSoup(fileHandle.read(), 'html.parser')

            info_dict = dict()
            info_dict['Nome'] = html.find('fieldset').find('b').text.strip('\n ').replace(u'\xa0', u'')

            # Read the two main tables containing name, address, contact and certification information
            info_table = html.find('fieldset').find_all('table')[2]
            info_table2 = html.find('fieldset').find_all('table')[-1]

            # Create a dictionary with the provider's information
            product_dict = {}

            # Iterates over the first table rows
            for row in info_table.find_all('tr'):
                tds = row.find_all('td')
                info_dict[tds[0].text.strip('\n :')] = tds[1].text.strip('\n ')

                if tds[0].text.strip('\n :') == 'Estado' or tds[0].text.strip('\n :') == 'Fone':
                    info_dict[tds[2].text.strip('\n :')] = re.sub(' +', ' ',
                                                                  tds[3].text.strip('\n ').replace('\n', ' '))

            # Iterates over the second table rows
            for row in info_table2.find_all('tr'):
                tds = row.find_all('td')
                info_dict[tds[0].text.strip('\n :')] = re.sub(' +', ' ', tds[1].text.strip('\n ').replace('\n', ' '))

                # Creates a list, splitting the categories/classes information of the provider
                if tds[0].text.strip('\n :') == 'Categorias/Classes':
                    if ', ' in info_dict[tds[0].text.strip('\n :')]:
                        info_dict[tds[0].text.strip('\n :')] = info_dict[tds[0].text.strip('\n :')].split(', ')
                    else:
                        info_dict[tds[0].text.strip('\n :')] = [re.sub(' +', ' ',
                                                                       tds[1].text.strip('\n ').replace('\n', ' ')), ]

                # Extracts needed information from the Operative Specification, Capabilities list and certificate
                elif tds[0].text.strip('\n :') == 'Espec. Operativa' \
                        and 'não disponível' not in info_dict[tds[0].text.strip('\n :')].lower() \
                        or tds[0].text.strip('\n :') == 'Lista de Capac.' \
                        and 'não disponível' not in info_dict[tds[0].text.strip('\n :')].lower() \
                        or tds[0].text.strip('\n :') == 'Certificado' \
                        and 'não disponível' not in info_dict[tds[0].text.strip('\n :')].lower():
                    info_dict[tds[0].text.strip('\n :')] = f"https://sistemas.anac.gov.br/certificacao/AvGeral/" \
                                                            f"{tds[1].find('a')['href']}"

            # Find the rest of fieldsets, containing information about Foreign co-validation and products serviced
            fs = html.find_all('fieldset')[1:]

            if len(fs) > 0:
                if 'NÃO EXISTEM PRODUTOS CADASTRADOS' not in fs[0].text:
                    fst = [re.sub('\n+', '|', el.text).split('|')[1].strip('\n :') for el in fs]

                    for fsi in range(len(fs)):
                        # Deals with the products
                        if fst[fsi] is not None and fst[fsi] != 'CONVALIDAÇÃO ESTRANGEIRA':
                            fset = fs[fsi]

                            p = fset.find_all('td')

                            pdict = {}
                            for i in range(0, int((len(p) + 1) / 5)):
                                el = re.sub('\n+', '|', p[5 * i + 3].text.replace(u'\xa0', u' ')
                                            ).split('|')[1].strip('\n :').split(', ')

                                for x in range(len(el)):
                                    el[x] = el[x].strip()

                                k = re.sub(' +', ' ',
                                           p[5 * i + 1].text.replace(u'\xa0', u' ').replace('\n', '').strip('\n :'))
                                pdict[k] = el

                            # Dict structured as 'Manufacturer': list of products.
                            product_dict[fst[fsi]] = pdict

                        # Extracts information about Foreign co-validation
                        elif fst[fsi] is not None and fst[fsi] == 'CONVALIDAÇÃO ESTRANGEIRA':
                            fset = fs[fsi]
                            rows = fset.select('tr[onmouseover]')

                            info_dict['Convalidações estrangeiras'] = []

                            for row in rows:
                                stub = 'https://sistemas.anac.gov.br/certificacao/AvGeral/'
                                info_dict['Convalidações estrangeiras'].append(
                                    dict(Autoridade=row.find('a').text.replace(u'\xa0', u' ').strip('\n :'),
                                         Link=stub + row.find('a')['href'],
                                         Validade=datetime.datetime(
                                            int(row.select('td:last-child')[0].text.strip(' \n').split()[2]),
                                            mdict[row.select('td:last-child')[0].text.strip(' \n').split()[1]],
                                            int(row.select('td:last-child')[0].text.strip(' \n').split()[0]),
                                        ))
                                )

                    # Assign a key to the dictionary of products found
                    info_dict['Produtos'] = product_dict

                else:
                    # A string saing there's no information is there for the cases where there are no products
                    info_dict['Produtos'] = fs[0].text.strip('\n ')
            else:
                info_dict['Produtos'] = dict()

            if type(info_dict['Produtos']) == dict:
                if len(info_dict['Produtos'].keys()) == 1 \
                        and 'NÃO EXISTEM PRODUTOS CADASTRADOS' in info_dict['Produtos'].keys():
                    info_dict['Produtos'] = 'NÃO EXISTEM PRODUTOS CADASTRADOS'

            # The dictionary of informations on the service provider is then appended to the list, along with the others
            emp_info_list.append(info_dict)
            n += 1
            print('\b'*len(s), end='')

        # Skip exception raised when dealing with wrong datatype
        except AttributeError:
            print('\b'*len(s), end='')
            continue

        # Skip exception raised when trying to read a folder
        except PermissionError:
            print('\b'*len(s), end='')
            continue

    print(f'\033[92mDone\033[0m '
          f'({len(emp_info_list)} HTML files parsed)')

    return emp_info_list


def providers_info_to_excel(parsed_html_info):
    """
    Takes the list of dictionaries provided by parse_providers_info and generates an Excel sheet containing the data
    split between tables as it would be in an SQL-type database.

    :param parsed_html_info: List of dictionaries containing the information parsed by parse_providers_info
    :return: None
    """
    data = parsed_html_info

    print(f'{timestamp()} Populate excel worksheet')

    # Create lists to track the number of unique occurrences
    category_list = []
    status_list = []
    product_type_list = []
    manufacturer_list = []

    print('    Create populating dictionaries', end='')

    # Iterate over the maintenance service providers info, appending the unique occurrences to the lists
    for service_provider in data:
        if isinstance(service_provider['Categorias/Classes'], list):
            for category in service_provider['Categorias/Classes']:
                if category not in category_list:
                    category_list.append(category)

        if service_provider['Status'] != '' and service_provider['Status'] not in status_list:
            status_list.append(service_provider['Status'])

        if isinstance(service_provider['Produtos'], dict):
            for product_type_key in service_provider['Produtos'].keys():
                if product_type_key not in product_type_list:
                    product_type_list.append(product_type_key)

                for manufacturer in service_provider['Produtos'][product_type_key].keys():
                    if manufacturer not in manufacturer_list:
                        manufacturer_list.append(manufacturer)

    # Lists are then sorted
    status_list.sort()
    category_list.sort()
    manufacturer_list.sort()
    product_type_list.sort()

    # Unique keys are provided to each unique information, corresponding to a database primary key
    # and mapped to dictionaries
    status_to_id_dict = {status_list[i]: i + 1 for i in range(len(status_list))}
    category_to_id_dict = {category_list[i]: i + 1 for i in range(len(category_list))}
    manufacturer_to_id_dict = {manufacturer_list[i]: i + 1 for i in range(len(manufacturer_list))}
    product_type_to_id_dict = {product_type_list[i]: i + 1 for i in range(len(product_type_list))}

#    # Dictionaries are also provided for the reverse procedure
#    id_to_status_dict = {i + 1: status_list[i] for i in range(len(status_list))}
#    id_to_category_dict = {i + 1: category_list[i] for i in range(len(category_list))}
#    id_to_manufacturer_dict = {i + 1: manufacturer_list[i] for i in range(len(manufacturer_list))}
#    id_to_product_type_dict = {i + 1: product_type_list[i] for i in range(len(product_type_list))}

    product_list = []

    for service_provider in data:
        if isinstance(service_provider['Produtos'], dict):
            for product_type_key in service_provider['Produtos'].keys():
                for manufacturer_key in service_provider['Produtos'][product_type_key]:
                    for product in service_provider['Produtos'][product_type_key][manufacturer_key]:
                        tup = (product_type_to_id_dict[product_type_key],
                               manufacturer_to_id_dict[manufacturer_key],
                               product)
                        if tup not in product_list:
                            product_list.append(tup)

    product_list.sort()
    product_to_id_dict = {product_list[i]: i + 1 for i in range(len(product_list))}
#    id_to_product_dict = {i + 1: product_list[i] for i in range(len(product_list))}

    print(' - \033[92mDone\033[0m')

    # Start creating the XMLX file, with sheets and setting the correct column sizes
    xlsx = xlsxwriter.Workbook(f'Oficinas ({str(datetime.datetime.now().strftime("%m-%d-%Y %H%M"))}).xlsx')
    service_providers_sheet = xlsx.add_worksheet('Oficinas')
    service_providers_sheet.set_column('A:A', 5)
    service_providers_sheet.set_column('B:B', 135)
    service_providers_sheet.set_column('C:C', 108)
    service_providers_sheet.set_column('D:D', 45)
    service_providers_sheet.set_column('E:E', 26)
    service_providers_sheet.set_column('F:F', 7)
    service_providers_sheet.set_column('G:G', 11)
    service_providers_sheet.set_column('H:H', 25)
    service_providers_sheet.set_column('I:I', 25)
    service_providers_sheet.set_column('J:J', 22)
    service_providers_sheet.set_column('K:K', 99)
    service_providers_sheet.set_column('L:L', 185)
    service_providers_sheet.set_column('M:M', 30)
    service_providers_sheet.set_column('N:N', 255)
    service_providers_sheet.set_column('O:O', 93)
    service_providers_sheet.set_column('P:P', 91)
    service_providers_sheet.set_column('Q:Q', 91)
    service_providers_sheet.set_column('R:R', 9)
    service_providers_sheet.set_column('S:S', 18)

    manufacturer_sheet = xlsx.add_worksheet('Fabricantes')
    manufacturer_sheet.set_column('A:A', 4)
    manufacturer_sheet.set_column('B:B', 73)

    category_sheet = xlsx.add_worksheet('Categorias')
    category_sheet.set_column('A:A', 3)
    category_sheet.set_column('B:B', 23)

    status_sheet = xlsx.add_worksheet('Status')
    status_sheet.set_column('A:A', 2)
    status_sheet.set_column('B:B', 15)

    products_sheet = xlsx.add_worksheet('Produtos')
    products_sheet.set_column('A:A', 5)
    products_sheet.set_column('B:B', 18)
    products_sheet.set_column('C:C', 13)
    products_sheet.set_column('D:D', 28)

    product_type_sheet = xlsx.add_worksheet('Tipos_produtos')
    product_type_sheet.set_column('A:A', 2)
    product_type_sheet.set_column('B:B', 12)

    foreign_covalidation_sheet = xlsx.add_worksheet('Convalidações')
    foreign_covalidation_sheet.set_column('A:A', 5)
    foreign_covalidation_sheet.set_column('B:B', 10)
    foreign_covalidation_sheet.set_column('C:C', 21)
    foreign_covalidation_sheet.set_column('D:D', 11)
    foreign_covalidation_sheet.set_column('E:E', 70)

    service_providers_products_sheet = xlsx.add_worksheet('Oficinas_Produtos')
    service_providers_products_sheet.set_column('A:A', 6)
    service_providers_products_sheet.set_column('B:B', 10)
    service_providers_products_sheet.set_column('C:C', 11)

    service_providers_category_classes_sheet = xlsx.add_worksheet('Oficinas_Categorias')
    service_providers_category_classes_sheet.set_column('A:A', 5)
    service_providers_category_classes_sheet.set_column('B:B', 10)
    service_providers_category_classes_sheet.set_column('C:C', 19)

    # Provide formatting to the datetime and date data types
    datetime_format = xlsx.add_format({'num_format': 'dd/mm/yyyy hh:mm:ss'})
    date_format = xlsx.add_format({'num_format': 'dd/mm/yyyy'})

    # Populate manufacturer_sheet
    print('    Populate manufacturer table - ', end='')
    manufacturer_sheet.write_row(0, 0, ('ID', 'Nome'))
    r = 1
    for key in manufacturer_to_id_dict:
        s = f'({r + 1}/{len(manufacturer_to_id_dict)} - {round((r + 1) / len(manufacturer_to_id_dict) * 100, 2)}%)'
        print(s, end='')
        manufacturer_sheet.write_row(r, 0, (manufacturer_to_id_dict[key], key))
        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate category_sheet
    print('    Populate category table - ', end='')
    category_sheet.write_row(0, 0, ('ID', 'Categoria/Classe'))
    r = 1
    for key in category_to_id_dict:
        s = f'({r + 1}/{len(category_to_id_dict)} - {round((r + 1) / len(category_to_id_dict) * 100, 2)}%)'
        print(s, end='')
        category_sheet.write_row(r, 0, (category_to_id_dict[key], key))
        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate status_sheet
    print('    Populate status table - ', end='')
    status_sheet.write_row(0, 0, ('ID', 'Status'))
    r = 1
    for key in status_to_id_dict:
        s = f'({r + 1}/{len(status_to_id_dict)} - {round((r + 1) / len(status_to_id_dict) * 100, 2)}%)'
        print(s, end='')
        status_sheet.write_row(r, 0, (status_to_id_dict[key], key))
        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate product_type_sheet
    print('    Populate product type table - ', end='')
    product_type_sheet.write_row(0, 0, ('ID', 'Tipo'))
    r = 1
    for key in product_type_to_id_dict:
        s = f'({r + 1}/{len(product_type_to_id_dict)} - {round((r + 1) / len(product_type_to_id_dict) * 100, 2)}%)'
        print(s, end='')
        product_type_sheet.write_row(r, 0, (product_type_to_id_dict[key], key))
        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate product_sheet
    print('    Populate product table - ', end='')
    products_sheet.write_row(0, 0, ('ID', 'Tipo de produto_ID', 'Fabricante_ID', 'Modelo'))
    r = 1
    for key in product_to_id_dict:
        s = f'({r + 1}/{len(product_to_id_dict)} - {round((r + 1) / len(product_to_id_dict) * 100, 2)}%)'
        print(s, end='')
        products_sheet.write_row(r, 0, (product_to_id_dict[key],) + key)
        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate providers_sheet
    print('    Populate maintenance service providers table - ', end='')
    data.sort(key=lambda x: x['Nome'])
    service_providers_sheet.write_row(0, 0, ('ID', 'Nome', 'Endereço', 'Complemento', 'Cidade', 'Estado', 'CEP', 'Fone',
                                             'FAX', 'País', 'Website', 'E-mail', 'Tipo de base', 'Serviços',
                                             'Certificado', 'Especificação Operativa', 'Lista de capacidades',
                                             'Status_ID', 'Última atualização'
                                             )
                                      )
    for i in range(len(data)):
        s = f'({i + 1}/{len(data)} - {round((i + 1) / len(data) * 100, 2)}%)'
        print(s, end='')
        data[i]['id'] = i + 1
        service_providers_sheet.write_row(i + 1, 0, (data[i]['id'],
                                                     data[i]['Nome'],
                                                     data[i]['Endereço'],
                                                     data[i]['Complemento'],
                                                     data[i]['Cidade'],
                                                     data[i]['Estado'],
                                                     data[i]['CEP'],
                                                     data[i]['Fone'],
                                                     data[i]['FAX'],
                                                     data[i]['País'],
                                                     data[i]['Website'],
                                                     data[i]['E-mail'],
                                                     data[i]['Tipo de Base'],
                                                     data[i]['Serviços'],
                                                     data[i]['Certificado'],
                                                     data[i]['Espec. Operativa'],
                                                     data[i]['Lista de Capac.'],
                                                     status_to_id_dict[data[i]['Status']],

                                                     ))
        service_providers_sheet.write(i+1, 18, datetime.datetime.now() - datetime.datetime(1899, 12, 31),
                                      datetime_format)

        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate foreign_covalidation_sheet
    print('    Populate foreign co-validation table - ', end='')
    foreign_covalidation_sheet.write_row(0, 0, ('ID', 'Oficina_ID', 'Autoridade Estrangeira', 'Validade', 'Link'))
    n = 1
    r = 1
    for service_provider in data:
        s = f'({n}/{len(data)} - {round(n / len(data) * 100, 2)}%)'
        print(s, end='')
        if 'Convalidações estrangeiras' in service_provider:
            for covalidation in service_provider['Convalidações estrangeiras']:
                foreign_covalidation_sheet.write_row(r, 0, (r,
                                                            service_provider['id'],
                                                            covalidation['Autoridade'],
                                                            ))
                foreign_covalidation_sheet.write(r, 3, covalidation['Validade'] - datetime.datetime(1899, 12, 31),
                                                 date_format)
                foreign_covalidation_sheet.write(r, 4, covalidation['Link'])
                r += 1
        n += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    # Populate the many to many relationship tables
    service_providers_category_classes_sheet.write_row(0, 0, ('ID', 'Oficina_ID', 'Categoria/Classe_ID'))
    service_providers_products_sheet.write_row(0, 0, ('ID', 'Oficina_ID', 'Produto_ID'))

    r = 1
    r1 = 1
    r2 = 1
    print('    Populate relationship tables - ', end='')
    for service_provider in data:
        # Service providers and categories/classes table
        s = f'({r + 1}/{len(data)} - {round((r + 1) / len(data) * 100, 2)}%)'
        print(s, end='')
        if isinstance(service_provider['Categorias/Classes'], list):
            for category in service_provider['Categorias/Classes']:
                service_providers_category_classes_sheet.write_row(r1, 0, (r1,
                                                                           service_provider['id'],
                                                                           category_to_id_dict[category]))
                r1 += 1

        # Service providers and products table
        if isinstance(service_provider['Produtos'], dict):
            for product_type_key in service_provider['Produtos']:
                for manufacturer_key in service_provider['Produtos'][product_type_key]:
                    for product in service_provider['Produtos'][product_type_key][manufacturer_key]:
                        service_providers_products_sheet.write_row(r2, 0,
                                                                   (r2,
                                                                    service_provider['id'],
                                                                    product_to_id_dict[(
                                                                        product_type_to_id_dict[product_type_key],
                                                                        manufacturer_to_id_dict[manufacturer_key],
                                                                        product)]
                                                                    )
                                                                   )
                        r2 += 1

        r += 1
        print('\b' * len(s), end='')
    print('\033[92mDone\033[0m')

    xlsx.close()
    print('\033[96m    Table population complete\033[0m\n')

    return None


# If running the module directly
if __name__ == '__main__':
    download_providers_info()
    providers_info_to_excel(parse_providers_info())
    print(f'{timestamp()} Cleaning up', end='')
    shutil.rmtree('html_empresas')
    print('\033[92m - Done\033[0m')
    print(f'{timestamp()} \033[92mAll done!\033[0m')
