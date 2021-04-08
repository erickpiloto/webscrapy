import requests
from bs4 import BeautifulSoup
from ast import literal_eval

URL_ALVO = "https://in*********ro.com.br"
URL_COMPRAR = "{}/comprar".format(URL_ALVO)
URL_AUTOMOVEIS = "{}/buscar/tipo.carro/anunciante.particular".format(URL_ALVO)

DADOS = {} # Dicionário para trabalhar com json caso precise futuramente


def salva_txt(dado):
    try:
        with open("dados_saida.txt", "a") as arquivo:
            arquivo.write(dado)
    except Exception as error:
        print("Erro ao salvar arquivo")
        print(error)


def requisicao(url):
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            resposta_html = resposta.text
            return resposta_html
        else:
            print("Erro ao fazer requisição")
    except Exception as error:
        print("Erro ao fazer requisição")
        print(error)


def parsing(resposta_html):
    try:
        soup = BeautifulSoup(resposta_html, 'html.parser')
        return soup
    except Exception as error:
        print("Erro ao fazer o parsing HTML")
        print(error)


def encontrar_links(soup):
    try:
        div_pai = soup.find("div", class_="vehicles-list-content")
        alvos = div_pai.find_all("a", class_="vehicle-thumbnail")
    except:
        print("Erro ao encontrar links")
        return None

    links = []
    for i in alvos:
        try:
            link = i['href']
            links.append(link)
        except:
            pass

    lista_links = list(filter(lambda x: x.startswith(URL_COMPRAR), links))
    return lista_links


def busca_dados(lista_links):
    while True:
        try:
            link_anuncio = lista_links.pop(0)
        except:
            return None

        html_anuncio = requisicao(link_anuncio)
        if html_anuncio:
            soup_anuncio = parsing(html_anuncio)
            if soup_anuncio:
                dados = soup_anuncio.find(class_="box-whatsapp")
                dados_a = dados.find("a")
                str_dados = dados_a.get("data-anunciante")
                dados_dic = literal_eval(str_dados)
                nome = dados_dic["nome"]
                cidade = dados_dic["regiao"]
                fone = soup_anuncio.find(class_="whatsapp-see number-phone")
                telefone = fone.get_text()
                saida = "{} - {} - {}\n".format(nome, telefone, cidade)
                salva_txt(saida)
                DADOS[nome] = {"Fone":telefone,"Cidade":cidade}


def main():
    print("Iniciando Raspagem da Página 1...")
    salva_txt("Raspagem do site: {}\n".format(URL_ALVO))
    salva_txt("URL TARGET: {}\n".format(URL_AUTOMOVEIS))
    salva_txt("----------------------------------------------------\n")
    contagem = 1
    html_anuncios = requisicao(URL_AUTOMOVEIS)
    if html_anuncios:
        soup_anuncios = parsing(html_anuncios)
        if soup_anuncios:
            links_anuncio = encontrar_links(soup_anuncios)
            if links_anuncio:
                busca_dados(links_anuncio)
                print("Dados Salvos! - Pág{}".format(contagem))
                salva_txt("------------------------------------ PÁGINA: {} ----------\n".format(contagem))
                print(DADOS)
                print("Fim da página {}".format(contagem))
                while True:
                    contagem += 1
                    print("Iniciando Página {}...".format(contagem))
                    link_prox = "{}?pagina={}".format(URL_AUTOMOVEIS, contagem)
                    try:
                        html_pag2 = requisicao(link_prox)
                        soup_pag2 = parsing(html_pag2)
                        links_pag2 = encontrar_links(soup_pag2)
                        if len(links_pag2) > 0:
                            busca_dados(links_pag2)
                            print("Dados Salvos! - Pág{}".format(contagem))
                            salva_txt("------------------------------------ PÁGINA: {} ----------\n".format(contagem))
                            print("Fim da página {}".format(contagem))
                        else:
                            print("Não existe mais páginas para obter dados.")
                            salva_txt("=== FIM ===")
                            print("Encerrando...")
                            break
                    except Exception as error:
                        print("Erro ao rodar programa!!!")
                        print(error)
                        print("Encerrando...")
                        break


main()

