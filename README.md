# Barber CRM API

API para gerenciamento de barbearias, barbeiros, clientes e agendamentos.

## Como Rodar

### Com Docker (Recomendado)

```bash
# Subir a aplicação
docker compose up -d

# Ver logs
docker compose logs -f api

# Parar
docker compose down
```

Acesse: http://localhost:8000

Docs interativos: http://localhost:8000/docs

### Local (Sem Docker)

```bash
# Requisitos: Python 3.11+

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar PostgreSQL e atualizar DATABASE_URL no .env

# Rodar
uvicorn app.main:app --reload
```

---

## Endpoints

### Usuarios /users
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /users | Criar usuario |
| GET | /users | Listar todos |
| GET | /users/{id} | Buscar por ID |
| PUT | /users/{id} | Atualizar |
| DELETE | /users/{id} | Deletar (soft delete) |
| POST | /users/{id}/restore | Restaurar usuario |

---

### Barbearias /barbershops
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barbershops | Criar barbearia |
| GET | /barbershops | Listar todas |
| GET | /barbershops/{id} | Buscar por ID |
| PUT | /barbershops/{id} | Atualizar |
| DELETE | /barbershops/{id} | Deletar (soft delete) |
| POST | /barbershops/{id}/restore | Restaurar barbearia |

---

### Clientes /customers
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /customers | Criar cliente |
| GET | /customers | Listar todos |
| GET | /customers/{id} | Buscar por ID |
| PUT | /customers/{id} | Atualizar |
| DELETE | /customers/{id} | Deletar (soft delete) |
| POST | /customers/{id}/restore | Restaurar cliente |

---

### Servicos /services
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /services | Criar servico |
| GET | /services/{id} | Buscar por ID |
| GET | /services/barbershop/{barbershop_id} | Listar por barbearia |
| GET | /services/barbershop/{barbershop_id}/active | Listar ativos |
| GET | /services/barbershop/{barbershop_id}/category/{category} | Filtrar por categoria |
| PUT | /services/{id} | Atualizar |
| DELETE | /services/{id} | Deletar |

---

### Barbeiros /barbers
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barbers | Criar barbeiro |
| GET | /barbers/{id} | Buscar por ID |
| GET | /barbers/user/{user_id} | Buscar por usuario |
| GET | /barbers/barbershop/{barbershop_id} | Listar por barbearia |
| GET | /barbers/barbershop/{barbershop_id}/active | Listar ativos |
| PUT | /barbers/{id} | Atualizar |
| DELETE | /barbers/{id} | Deletar |

---

### Horarios dos Barbeiros /barber-schedules
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barber-schedules | Criar horario |
| GET | /barber-schedules/{id} | Buscar por ID |
| GET | /barber-schedules/barber/{barber_id} | Listar por barbeiro |
| GET | /barber-schedules/barber/{barber_id}/available | Listar disponiveis |
| PUT | /barber-schedules/{id} | Atualizar |
| DELETE | /barber-schedules/{id} | Deletar |

---

### Agendamentos /appointments
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /appointments | Criar agendamento |
| GET | /appointments/{id} | Buscar por ID |
| GET | /appointments/barbershop/{barbershop_id} | Listar por barbearia |
| GET | /appointments/barbershop/{barbershop_id}/status/{status} | Filtrar por status |
| GET | /appointments/customer/{customer_id} | Listar por cliente |
| GET | /appointments/barber/{barber_id} | Listar por barbeiro |
| PUT | /appointments/{id} | Atualizar |
| DELETE | /appointments/{id} | Deletar |

---

### Perfil da Barbearia /barbershop-profiles
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barbershop-profiles | Criar perfil |
| GET | /barbershop-profiles/barbershop/{barbershop_id} | Buscar por barbearia |
| PUT | /barbershop-profiles/{id} | Atualizar |
| DELETE | /barbershop-profiles/{id} | Deletar (soft delete) |
| POST | /barbershop-profiles/{id}/restore | Restaurar |

---

### Horario de Funcionamento /barbershop-schedules
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barbershop-schedules | Criar horario |
| GET | /barbershop-schedules/barbershop/{barbershop_id} | Buscar por barbearia |
| PUT | /barbershop-schedules/{id} | Atualizar |
| DELETE | /barbershop-schedules/{id} | Deletar (soft delete) |
| POST | /barbershop-schedules/{id}/restore | Restaurar |

---

### Configuracoes /barbershop-settings
| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | /barbershop-settings | Criar configuracoes |
| GET | /barbershop-settings/{id} | Buscar por ID |
| GET | /barbershop-settings/barbershop/{barbershop_id} | Buscar por barbearia |
| PUT | /barbershop-settings/{id} | Atualizar |
| DELETE | /barbershop-settings/{id} | Deletar (soft delete) |
| POST | /barbershop-settings/{id}/restore | Restaurar |

---

## Testes

```bash
# Rodar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Estrutura

```
app/
├── api/          # Rotas/endpoints
├── core/         # Configuracoes
├── db/           # Database/session
├── models/       # SQLAlchemy models
├── repositories/ # Acesso a dados
├── schemas/      # Pydantic schemas
└── services/     # Regras de negocio
tests/            # Testes
```
