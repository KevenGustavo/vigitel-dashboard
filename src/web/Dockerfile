# ─── Estágio 1: Build do Frontend com Node.js ───────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copia manifestos de dependência
COPY package*.json ./

# Instala dependências de forma reproduzível
RUN npm ci

# Copia o restante do código da aplicação
COPY . .

# Executa testes unitários na esteira de build
RUN npm test

# Compila o bundle otimizado de produção com Vite
RUN npm run build

# ─── Estágio 2: Servidor Nginx de Alta Performance ─────────────
FROM nginx:1.27-alpine

# Remove a configuração padrão do Nginx
RUN rm -rf /etc/nginx/conf.d/default.conf

# Copia a configuração otimizada com Gzip, cache e headers de segurança
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia os artefatos compilados do estágio de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Expõe a porta 80 padrão HTTP
EXPOSE 80

# Inicia o Nginx
CMD ["nginx", "-g", "daemon off;"]
