# Sistema de Cadastro

Aplicação desktop de estudo para cadastrar, consultar, editar e remover contatos. Feita com Python, Tkinter e SQLite, sem dependências externas.

## Funcionalidades

- Cadastrar nome, e-mail e telefone
- Listar registros salvos
- Buscar por nome, e-mail ou telefone
- Selecionar um registro para editar ou excluir
- Validar campos obrigatórios e impedir e-mails duplicados
- Salvar dados em um banco SQLite local

## Requisitos

- Python 3.10 ou superior
- Tkinter, normalmente incluído na instalação do Python para Windows

## Como executar

```bash
python app.py
```

O banco `contatos.db` é criado automaticamente na primeira execução e permanece no computador. Ele não deve ser enviado ao repositório; o arquivo está coberto pelo `.gitignore`.

## Estrutura

```text
sistema-cadastro-python/
├── app.py
├── README.md
└── .gitignore
```

## Próximos passos de aprendizagem

- Separar a interface da camada de persistência
- Adicionar testes para validação e operações de banco
- Criar capturas de tela e documentar decisões de projeto

