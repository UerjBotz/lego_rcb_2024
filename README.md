# Carcará Branco

Repositório criado para o desafio RCB Challenge Kit da CBR 2024 (antigo SEK).

## Pré-requisitos

Usamos o vscode no Ubuntu 24.04 com o pybricksdev para o upload e desenvolvimento do código e um SPIKE Prime Hub, da LEGO, como alvo.

Certifique-se de ter o Python 3 instalado na sua máquina. Você pode verificar a versão do Python com o comando:

```bash
python --version
```

A seção seguinte é baseada no tutorial oficial da pybricks sobre o uso de outros editores.

Fonte: <https://pybricks.com/project/pybricks-other-editors/>


## Configurando o Ambiente

Este projeto utiliza um ambiente virtual para gerenciar dependências de forma isolada. Siga as instruções abaixo para configurar o ambiente.

### Passo 1: Crie o Ambiente Virtual

Crie um ambiente virtual na pasta do projeto (normalmente chamado de `.venv`):

```bash
python -m venv .venv
```

### Passo 2: Ative o Ambiente Virtual

Após criar o ambiente virtual, ative-o.
```bash
  .venv/bin/activate
```

> **Nota**: Após ativar o ambiente, você verá o prefixo `(.venv)` antes do prompt do terminal, indicando que o ambiente virtual está ativo.

### Passo 3: Instale as Dependências

Instale as dependências do projeto listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

Agora seu ambiente virtual está configurado e pronto para uso!


## Executando o Projeto

Aperte F5 no VSCode para rodar o projeto.

## Contribuição

### Interna
Se desejar contribuir com o projeto, faça um clone do repositório, crie uma branch com a sua feature, e envie um push para a sua branch. **Não comite para a master** 

1. Faça o clone do projeto (`git clone https://github.com/UerjBotz/lego_rcb_2024.git`)
2. Crie uma branch para sua feature (`git checkout -b nome-da-sua-branch`)
3. Adicione suas mudanças (`git add $arquivo1 $arquivo2 ... $arquivoN`)
4. Comite suas mudanças explicando o que/porque mudou (`git commit`) com uma mensagem descritiva.
5. Faça o push para a branch (`git push origin nome-da-sua-branch`)
6. Abra um Pull Request


### Externa 
1. Faça o fork do projeto
2. Siga os passos para a contribuição interna

Qualquer dúvida, entre em contato ou abra uma issue no repositório.
