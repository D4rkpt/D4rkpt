# D4RKPT / Mission Control — instalação

## O que estás a receber

- README.md final, em inglês para ser legível por uma audiência internacional.
- Banner SVG original, com animação subtil e alternativa sem movimento quando suportada.
- Dashboard local com variantes claras e escuras.
- Calendário de contributos, distribuição de linguagens, quatro projetos e seis eventos recentes.
- Script Python sem dependências pip; recolhe dados da API oficial do GitHub.
- Dois workflows: sincronização do perfil e geração do Commit Invaders.
- LICENSE apenas para o código e design originais deste pacote.

A animação arcade é da autoria de Goblinlordx, não foi criada por este pacote. Os SVGs gerados pelo projeto upstream são publicados na branch output, separada da main.

## 1. Criar o repositório correto

Na conta D4rkpt, cria um repositório PÚBLICO chamado D4rkpt.
O resultado deve ser D4rkpt/D4rkpt. Usa main como branch predefinida.
Se já existir, guarda uma cópia do conteúdo atual antes de substituir ficheiros.

## 2. Adicionar TODOS os ficheiros

Extrai o ZIP e copia o conteúdo da sua pasta de topo para a raiz do repositório.
Não coloques o pacote dentro de uma subpasta do repositório.
Inclui a pasta oculta .github; upload no navegador pode omitir pastas ocultas.

Estrutura:

README.md
SETUP.md
LICENSE
.gitignore
assets/
  hero.svg
  dashboard.svg
  dashboard-dark.svg
  contributions.svg
  contributions-dark.svg
  languages.svg
  languages-dark.svg
  project-1.svg
  project-1-dark.svg
  project-2.svg
  project-2-dark.svg
scripts/
  update_profile.py
.github/
  workflows/
    profile-sync.yml
    commit-invaders.yml

Exemplo se usares Git localmente, num repositório vazio já criado:

```bash
git clone https://github.com/D4rkpt/D4rkpt.git
cd D4rkpt
# Copia aqui os ficheiros extraídos, incluindo .github.
git add .
git commit -m "feat: add mission control profile"
git branch -M main
git push -u origin main
```

Não executes estes comandos cegamente sobre trabalho existente: revê o diff antes do commit.

## 3. Ativar e executar as automações

1. Abre o separador Actions e ativa workflows, caso apareça esse pedido.
2. Executa Profile / Mission Control Sync > Run workflow > main.
3. Executa Profile / Commit Arcade > Run workflow > main.
4. Espera que ambos terminem com sucesso.
5. Abre https://github.com/D4rkpt para ver o perfil.

O GITHUB_TOKEN é criado automaticamente por GitHub Actions e passado pelos workflows.
Não deves colar um token no README, no script ou no YAML.
Os workflows pedem apenas contents: write. Políticas da conta/organização podem restringir essa permissão.
Se o push falhar por permissões, verifica Settings > Actions > General > Workflow permissions e as regras de proteção da branch.
Não desatives proteção importante indiscriminadamente: se main exigir PRs, adapta a publicação a esse processo.

Os workflows usam referências de versão (@v4 e @v1). Para maior segurança da cadeia de fornecimento, fixa cada ação a um SHA completo que tenhas verificado e mantém-o atualizado.

## 4. Frequência e comportamento

- Perfil: diariamente às 06:23 UTC, ou por execução manual.
- Arcade: diariamente às 06:47 UTC, ou por execução manual.
- Edição do README, script ou workflow na main também pode iniciar a sincronização.
- Alteração do workflow arcade na main também pode iniciar a geração arcade.
- A agenda não promete atualização ao segundo; pode haver atrasos de execução.
- Sem alterações, o workflow de perfil não cria um novo commit.
- O commit do bot inclui [skip ci]; além disso, pushes com o GITHUB_TOKEN não iniciam normalmente novos workflows de push.
- SVGs podem ficar em cache no navegador/GitHub: uma atualização pode demorar a ser visível.
- O arcade só aparece quando o primeiro workflow correspondente criar os SVGs na branch output.

## 5. Privacidade e definições dos números

O script consulta apenas /users/{username}/repos e /events/public, e filtra ainda private=false.
Nunca publica nomes ou descrições de repositórios privados.
Não lhe dês um PAT com acesso a projetos privados: não é necessário para este perfil.
O calendário representa a visibilidade dos contributos que o GitHub disponibiliza para esse utilizador; pode incluir contagens anonimizadas de contributos privados dependendo das definições de visibilidade. Não publica código privado.

- Contributos NÃO significa commits. O dashboard usa totalContributions do calendário GraphQL.
- Projetos elegíveis: públicos, originais, não arquivados, excluindo o próprio repositório do perfil.
- Cartões: até quatro projetos, ordenados pela data do último push; não são os pinned repositories.
- Stars: soma dos repositórios elegíveis.
- Linguagens: bytes detetados pelo GitHub em até 40 projetos elegíveis, por último push. Não é experiência, domínio, tempo de utilização nem lista das linguagens que estudas.
- Eventos: até seis eventos recentes do feed público, consultando no máximo os primeiros 100 e excluindo o repositório do perfil. Não é um histórico completo de commits.
- Nenhuma métrica é inventada quando a API falha: o workflow falha e a última versão publicada mantém-se.

Os cartões iniciais têm os dois projetos públicos identificados durante a preparação. O calendário e as linguagens mostram uma mensagem de primeira sincronização; não contêm números simulados.

## 6. Personalizar

- Biografia: edita a secção The person behind the code.
- Tecnologias: edita Technology arsenal; não depende da deteção automática de linguagens.
- Cores: assets/hero.svg e PALETTE em scripts/update_profile.py.
- Projetos: repos[:4] em project_markup e no loop de renderização.
- Amostra de linguagens: repos[:40].
- Atividade: limite de seis eventos em activity_markup.
- Horário: cron nos dois YAML, sempre em UTC.
- Não apagues os pares de marcadores SNAPSHOT, PROJECTS e ACTIVITY; o script escreve entre eles.
- Não alteres só os SVGs do dashboard: serão regenerados; muda o script.
- Não incluí Discord pessoal, email, Spotify ou WakaTime porque não foram fornecidos. Nunca publiques links ou métricas fictícias.

## 7. Copiar para outra conta

Substitui D4rkpt no README e este guia pelo novo username.
Cria username/username e copia todos os ficheiros.
O workflow escolhe PROFILE_USERNAME a partir de github.repository_owner.
O nome de perfil no hero.svg também é manual: altera D4RKPT e a linha PORTUGAL se necessário.
O caminho da imagem arcade tem de apontar para username/username/output.
Preserva a atribuição a Goblinlordx/commit-invaders.

## 8. Limites do GitHub README

O README não executa uma aplicação JavaScript arbitrária. O efeito visual usa imagens SVG, Markdown, tabelas e HTML compatível.
O Commit Invaders é uma animação, não um jogo controlável com teclado no README.
O link de demo permite explorar a animação fora do GitHub; não se apresenta aqui como jogo completo jogável.
Os ícones e badges externos dependem de jsDelivr e Shields.io; o núcleo visual e as métricas principais ficam no repositório.
Não existe uma promessa científica de "dopamina": o design procura impacto, clareza, contraste e boa hierarquia.

## Inspiração e créditos

- Sindre Sorhus: identidade pessoal concisa e ligação ao trabalho real.
  https://github.com/sindresorhus/sindresorhus
- Anurag Hazra: apresentação, projetos em destaque e estatísticas.
  https://github.com/anuraghazra/anuraghazra
- Goblinlordx: Commit Invaders, sob licença MIT upstream.
  https://github.com/Goblinlordx/commit-invaders
- Devicon: ícones de tecnologias. https://github.com/devicons/devicon
- Shields.io: badges. https://shields.io
- Documentação do perfil: https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme

O texto, o banner e o gerador deste pacote são originais; não são cópias de perfis de terceiros.
