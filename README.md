# PrintMonitor

**Sistema de monitoramento de impressoras 3D**

## Sobre o projeto

O PrintMonitor é um projeto desenvolvido em Python e Django com o objetivo de criar uma plataforma web para monitoramento e gerenciamento de impressões 3D.

A aplicação utilizará a API do OctoPrint para obter informações da impressora e apresentá-las em um dashboard de fácil visualização.

Inicialmente, o projeto será desenvolvido e testado com uma Creality Ender 3 V3 SE conectada ao OctoPrint.

## Objetivos

O principal objetivo é centralizar informações importantes sobre o funcionamento da impressora, permitindo acompanhar impressões e consultar dados sem precisar acessar diretamente a interface do OctoPrint.

## Funcionalidades planejadas

- **Monitoramento em tempo real:** acompanhar o status da impressora.
- **Temperaturas:** visualizar as temperaturas do bico e da mesa.
- **Progresso da impressão:** acompanhar o percentual concluído e o tempo restante.
- **Histórico de impressões:** registrar trabalhos realizados e seus respectivos resultados.
- **Controle de custos:** estimar o consumo de filamento e o custo de cada impressão.
- **Notificações:** receber alertas sobre conclusão, interrupções e problemas durante as impressões.

As funcionalidades serão implementadas gradualmente, conforme a evolução do projeto.

## Tecnologias utilizadas

- Python
- Django
- Django REST Framework
- PostgreSQL
- HTML, CSS e JavaScript
- API do OctoPrint
- Docker

## Arquitetura inicial

O projeto será dividido em aplicações Django, cada uma com responsabilidades específicas:

| Aplicação | Responsabilidade |
|---|---|
| `core` | Página inicial e funcionalidades gerais |
| `printer` | Dados e configurações da impressora |
| `monitoring` | Monitoramento e processamento de informações |

## Acesso

O sistema será desenvolvido inicialmente para uma única impressora, com acesso pela rede local e possibilidade de acesso remoto através do Tailscale.

## Status do desenvolvimento

**Em desenvolvimento — versão 0.1.0**

Atualmente, o projeto está na fase de estruturação inicial, configuração do ambiente Django e organização da arquitetura.

## Objetivo futuro

A longo prazo, a proposta é transformar o PrintMonitor em uma ferramenta open source, permitindo que outros usuários de impressoras 3D possam utilizá-la, contribuir com seu desenvolvimento e adaptar suas funcionalidades às próprias necessidades.