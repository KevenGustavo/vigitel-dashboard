# 🔐 Guia de Configuração de Secrets para a CI/CD Pipeline

Este documento orienta o cadastro das variáveis de ambiente e segredos (**Secrets**) no seu repositório GitHub para ativar os deploys contínuos automatizados no **Render** (Back-end) e na **Vercel** (Front-end).

---

## Como cadastrar os Secrets no GitHub

1. No repositório do projeto no GitHub, clique na aba **Settings** (Configurações).
2. Na barra lateral esquerda, expanda **Secrets and variables** e clique em **Actions**.
3. Clique no botão verde **New repository secret**.
4. Insira o **Name** (Nome) e o **Secret** (Valor) correspondente e clique em **Add secret**.

---

## 1. Back-end API (Render Deploy)

| Secret Name | Obrigatório? | Descrição |
| :--- | :---: | :--- |
| `RENDER_DEPLOY_HOOK_URL` | Opcional | URL do Webhook de Deploy do Render para atualizar a API automaticamente. |

### Como obter o `RENDER_DEPLOY_HOOK_URL`:
1. Acesse o painel do [Render Dashboard](https://dashboard.render.com/).
2. Abra o serviço web da API (`vigitel-api`).
3. Acesse a aba **Settings** do serviço.
4. Role a página até a seção **Deploy Hook**.
5. Clique em **Create Deploy Hook**, defina o branch como `master` e copie a URL gerada (formato: `https://api.render.com/deploy/srv-xxxx?key=yyyy`).
6. Cadastre essa URL no GitHub com o nome `RENDER_DEPLOY_HOOK_URL`.

---

## 2. Front-end Web (Vercel Deploy)

| Secret Name | Obrigatório? | Descrição |
| :--- | :---: | :--- |
| `VERCEL_TOKEN` | Opcional | Token de autenticação pessoal da CLI da Vercel. |
| `VERCEL_ORG_ID` | Opcional | ID da Organização ou Usuário na Vercel. |
| `VERCEL_PROJECT_ID` | Opcional | ID do projeto criado na Vercel para o `vigitel-monitor`. |

### Como obter as chaves da Vercel:
1. **`VERCEL_TOKEN`**: Acesse [Vercel Account Tokens](https://vercel.com/account/tokens) -> clique em **Create Token** -> copie o token gerado.
2. **`VERCEL_ORG_ID` e `VERCEL_PROJECT_ID`**:
   - No seu terminal local, dentro da pasta `src/web`, rode:
     ```bash
     npx vercel link
     ```
   - Siga as instruções na tela para vincular ao seu projeto. O comando criará um arquivo local `.vercel/project.json` contendo `"orgId"` e `"projectId"`.
   - Copie esses valores para os secrets `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID`.

---

## 3. Banco de Dados para CI (Opcional)

| Secret Name | Obrigatório? | Descrição |
| :--- | :---: | :--- |
| `DATABASE_URL` | Opcional | URL de conexão PostgreSQL da instância remota (Neon DB). |

> [!NOTE]
> **Você não é obrigado a cadastrar o `DATABASE_URL` no GitHub**:
> A pipeline de CI foi configurada com um **Service Container** do PostgreSQL 15 local e um script de seed automático ([`sql/ci_test_schema.sql`](file:///home/keven/Projetos/vigitel-dashboard/sql/ci_test_schema.sql)). Os testes do back-end rodam de forma 100% isolada e autônoma sem depender de nenhuma chave externa.
> Caso cadastre o `DATABASE_URL`, o GitHub Actions rodará os testes de integração diretamente contra a sua instância Neon.
