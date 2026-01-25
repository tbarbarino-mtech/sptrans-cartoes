#!/usr/bin/env bash
set -euo pipefail

# Uso:
# ./setup_repo_and_auto_pr.sh <github-owner> <repo-name> "<repo-description>" [private|public] [main_branch_name]
#
# Exemplo:
# ./setup_repo_and_auto_pr.sh tbarbarino-mtech sptrans-cartoes "SPTrans Cartoes" private main

OWNER="${1:-}"
REPO="${2:-}"
DESCRIPTION="${3:-Repository created via script}"
VISIBILITY="${4:-private}"
MAIN_BRANCH="${5:-main}"

if [[ -z "$OWNER" || -z "$REPO" ]]; then
  echo "Uso: $0 <owner> <repo-name> \"<description>\" [private|public] [main_branch_name]"
  exit 2
fi

REMOTE_SSH="git@github.com:${OWNER}/${REPO}.git"

# 1) Criar repo no GitHub se não existir
echo "Verificando repositório ${OWNER}/${REPO}..."
if gh repo view "${OWNER}/${REPO}" >/dev/null 2>&1; then
  echo "Repositório já existe no GitHub."
else
  echo "Criando repositório ${OWNER}/${REPO}..."
  gh repo create "${OWNER}/${REPO}" --${VISIBILITY} --description "${DESCRIPTION}" --confirm
fi

# 2) Inicializar git local se necessário
if [ ! -d .git ]; then
  echo "Inicializando repositório git local..."
  git init
fi

# 3) Garantir branch main local
if ! git show-ref --verify --quiet "refs/heads/${MAIN_BRANCH}"; then
  echo "Criando branch ${MAIN_BRANCH} localmente..."
  git checkout -b "${MAIN_BRANCH}"
else
  git checkout "${MAIN_BRANCH}"
fi

# 4) Adicionar remote origin se ausente
if ! git remote | grep -q '^origin$'; then
  echo "Adicionando remote origin -> ${REMOTE_SSH}"
  git remote add origin "${REMOTE_SSH}"
fi

# 5) Commit inicial se não houver commits
if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "Criando commit inicial com README, requirements e .gitignore..."
  cat > README.md <<EOF
# ${REPO}

Repositório inicializado por script.
EOF

  cat > requirements.txt <<EOF
fastapi==0.95.2
uvicorn==0.22.0
pydantic==1.10.11
motor==4.4.0
pymongo==4.6.1
pytest==7.4.0
mongomock==4.1.2
python-dotenv==1.0.1
httpx==0.24.1
EOF

  cat > .gitignore <<EOF
__pycache__/
.venv/
.env
*.pyc
.idea/
.vscode/
EOF

  git add README.md requirements.txt .gitignore
  git commit -m "chore: initial commit (README, requirements, .gitignore)"
fi

# 6) Push main
echo "Fazendo push da branch ${MAIN_BRANCH}..."
git push -u origin "${MAIN_BRANCH}"

# 7) Criar release a partir de main se não existir
if git show-ref --verify --quiet refs/heads/release; then
  echo "Branch release já existe localmente."
else
  echo "Criando branch release a partir de ${MAIN_BRANCH}..."
  git checkout -b release "${MAIN_BRANCH}"
  git push -u origin release
fi

# 8) Criar develop a partir de main se não existir
if git show-ref --verify --quiet refs/heads/develop; then
  echo "Branch develop já existe localmente."
else
  echo "Criando branch develop a partir de ${MAIN_BRANCH}..."
  git checkout -b develop "${MAIN_BRANCH}"
  git push -u origin develop
fi

# 9) Voltar para develop
git checkout develop

# 10) Adicionar workflow GitHub Actions para criar PR develop -> release
WORKFLOW_DIR=".github/workflows"
WORKFLOW_FILE="${WORKFLOW_DIR}/auto-pr-develop-to-release.yml"

mkdir -p "${WORKFLOW_DIR}"

cat > "${WORKFLOW_FILE}" <<'YAML'
name: Auto PR from develop to release

on:
  push:
    branches:
      - develop

permissions:
  contents: write
  pull-requests: write

jobs:
  create_pr:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Create or update PR develop -> release
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: "chore: sync develop -> release"
          branch: "auto/pr-develop-to-release"
          base: "release"
          title: "chore: merge develop into release"
          body: |
            This PR was created automatically from develop to release.
            Review and merge when ready.
          labels: automated, sync
          delete-branch: true
YAML

# 11) Commit e push workflow
git add "${WORKFLOW_FILE}"
git commit -m "chore(ci): add workflow to auto-create PR from develop to release" || echo "Sem mudanças para commitar"
git push origin develop

# 12) Criar PR inicial (se não existir)
echo "Criando PR inicial develop -> release (se não existir)..."
gh pr create --base release --head develop --title "chore: merge develop into release" --body "Initial PR: merge develop into release" --label "auto-pr" || true

echo "Setup concluído. Repositório: https://github.com/${OWNER}/${REPO}"
echo "Branches criadas: ${MAIN_BRANCH}, develop, release"
echo "Workflow adicionado: ${WORKFLOW_FILE}"