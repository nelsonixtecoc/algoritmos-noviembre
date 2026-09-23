# Hitos y Entregas - Cronograma 4 Semanas

## Resumen de Hitos

| Hito | Nombre | Deadline | Estado |
|------|--------|----------|--------|
| H0 | Setup & Fundación | Día 2 | ⬜ Pendiente |
| H1 | Core Jugable | Fin Semana 1 | ⬜ Pendiente |
| H2 | Combate Básico | Fin Semana 2 | ⬜ Pendiente |
| H3 | Mundo Conectado | Fin Semana 3 | ⬜ Pendiente |
| H4 | Juego Completo | Fin Semana 4 | ⬜ Pendiente |

---

## H0: Setup & Fundación (Días 1-2)

### Objetivo
Repositorio funcional, equipo sincronizado, pipeline de desarrollo listo.

### Tareas
- [ ] Crear repo GitHub/GitLab (privado para la clase)
- [ ] `.gitignore` (Python, pygame, __pycache__, .venv, *.pyc, build/, dist/)
- [ ] `requirements.txt`:
  ```txt
  pygame>=2.5.0
  pytmx>=3.30  # solo si usan Tiled
  ```
- [ ] Configurar `ruff` + `black` (opcional pero recomendado):
  ```bash
  pip install ruff black
  ruff check .
  black .
  ```
- [ ] `main.py` esqueleto: init pygame, ventana 640×480, bucle 60 FPS, salir con ESC
- [ ] `config.py` con constantes base
- [ ] Definir convención de commits (Conventional Commits):
  - `feat:` nueva feature
  - `fix:` bug fix
  - `refactor:` refactor sin cambio funcional
  - `docs:` documentación
  - `style:` formato, lint
  - `test:` tests
- [ ] Crear tablero GitHub Projects / Trello / Notion con columnas: Backlog → To Do → In Progress → Review → Done
- [ ] Asignar issues iniciales a cada integrante
- [ ] Daily standup 15 min (presencial o Discord)

### Criterios de Aceptación
- `python main.py` abre ventana, muestra FPS 60, cierra limpio
- Todos clonan repo, crean venv, instalan deps, corren sin errores
- Tablero tiene 1 issue por módulo de la Semana 1

---

## H1: Core Jugable (Fin Semana 1 - Día 7)

### Objetivo
Jugador se mueve en mundo con colisiones, cámara sigue, state machine funcional.

### Tareas por Integrante

| Integrante | Tareas |
|------------|--------|
| **Core (1)** | `core/game.py` StateMachine completa, `core/camera.py` follow + límites, `core/events.py` bus básico |
| **Player (2)** | `entities/entity.py` base, `entities/player.py` movimiento 8 dirs + colisión walls, animaciones placeholder |
| **Enemigos (3)** | `entities/enemy.py` base (sin IA aún), `systems/pathfinding.py` esqueleto A* |
| **Mundo (4)** | `world/tilemap.py` carga CSV/TMX, render capas, colisión `walls` layer; 2 habitaciones test |
| **UI (5)** | `ui/hud.py` esqueleto (dibuja corazones placeholder), `ui/menus.py` MainMenu + PauseMenu funcionales |
| **Assets (6)** | Placeholders TODOS: player (rect colors), tiles (wall/ground), enemies, UI (corazón, moneda) |

### Integración (Día 6-7)
- Mergear todo a `main` via PRs
- Testing: Player nace en Room A, se mueve, choca paredes, cámara sigue, ESC → Pause, click → Resume

### Criterios de Aceptación
- [ ] Ventana 640×480, 60 FPS estable
- [ ] Player: WASD/arrows mueve 8 dirs, no atraviesa paredes
- [ ] Cámara: centra en player, no muestra fuera de bounds
- [ ] Estados: MENU → PLAYING → PAUSED → PLAYING → MENU
- [ ] 2 habitaciones cargadas (aunque vacías)
- [ ] Zero warnings lint

---

## H2: Combate Básico (Fin Semana 2 - Día 14)

### Objetivo
Combate funcional: player ataca → enemigos reciben daño → mueren → dropean pickups.

### Tareas por Integrante

| Integrante | Tareas |
|------------|--------|
| **Core (1)** | `core/save_load.py` save/load JSON (pos, hp, coins, keys, current_room) |
| **Player (2)** | Ataque espada (hitbox, cooldown, anim), invulnerabilidad 1s (flash), knockback, stats (hp, atk) |
| **Enemigos (3)** | 3 tipos funcionales: `Walker`, `Shooter`, `Charger` con IA básica + pathfinding simple |
| **Mundo (4)** | `world/room.py` spawn enemies/pickups, `world/dungeon.py` grafo 4 rooms + transiciones |
| **UI (5)** | HUD completo: corazones (3), contador monedas, llaves; sonidos básicos integrados |
| **Assets (6)** | Sprites finales: player (idle/walk/attack/hurt), 3 enemigos, tiles variados, pickups |

### Integración (Día 13-14)
- Playtest interno: completar dungeon 4 rooms, matar todos enemigos, recoger items
- Balanceo inicial: HP player/enemigos, daño espada, rate of fire shooter

### Criterios de Aceptación
- [ ] Player ataca (espacio/click) → hitbox frontal → enemigo pierde HP
- [ ] Enemigo muere → animación death → drop moneda/corazón aleatorio
- [ ] 3 tipos enemigos con comportamiento distinto
- [ ] Player recibe daño → flash rojo → knockback → invulnerabilidad 1s
- [ ] 3 corazones UI: pierdes 1 por golpe, 0 = Game Over (por ahora reinicia room)
- [ ] Monedas/llaves se cuentan en HUD
- [ ] Transiciones room→room funcionan
- [ ] Save/load: cierras juego → abres → estás en misma room con mismos stats

---

## H3: Mundo Conectado (Fin Semana 3 - Día 21)

### Objetivo
Dungeon completo con llaves/puertas, boss room accesible, HUD/menús pulidos.

### Tareas por Integrante

| Integrante | Tareas |
|------------|--------|
| **Core (1)** | Polish state transitions, bugfixes cross-module, code review intensivo |
| **Player (2)** | Polish movimiento (esquinas, deslizamiento), ataque cargado opcional, más animaciones |
| **Enemigos (3)** | `entities/boss.py` completo con 3 fases, arena boss room, tuning HP/daño/patrones |
| **Mundo (4)** | Dungeon final: 6 rooms, 2 llaves → 2 puertas → boss room; decoración, variedad |
| **UI (5)** | Game Over screen, Victory screen, minimapa opcional, screen shake, partículas simples |
| **Assets (6)** | Boss sprites + animaciones, tileset completo, sonidos finales, música 2 tracks |

### Integración (Día 20-21)
- Playtest completo: new game → dungeon → boss → victory → game over → retry
- Bug bash: cada integrante testa 30 min, reporta issues

### Criterios de Aceptación
- [ ] 6 rooms conectadas lógicamente (llave A abre puerta A, etc.)
- [ ] Boss room: se desbloquea con 2da llave, boss spawn al entrar
- [ ] Boss: 3 fases distintas, patterns claros, defeatable sin cheese
- [ ] Game Over: 0 HP → screen → "Volver a empezar" → reinicia desde room 1 con stats base
- [ ] Victory: boss muere → pantalla victoria → stats finales → main menu
- [ ] HUD: no bugs visuales, corazones correctos, monedas persisten
- [ ] Sonidos: todos los eventos tienen feedback auditivo
- [ ] Performance: 60 FPS en máquina modesta

---

## H4: Juego Completo (Fin Semana 4 - Día 28)

### Objetivo
Build final distribuible, documentación, testing exhaustivo, entrega.

### Tareas por Integrante

| Integrante | Tareas |
|------------|--------|
| **Core (1)** | `pyinstaller --onefile --windowed --add-data "assets;assets" main.py`, test .exe en Windows limpio |
| **Player (2)** | Balanceo final: playtest 10 runs, ajustar HP/damage/enemy count en `config.py` |
| **Enemigos (3)** | Bugfixes boss edge cases (stuck, invulnerabilidad, fase transitions) |
| **Mundo (4)** | Polish level design: checkpoints visuales, secret room opcional, flow natural |
| **UI (5)** | Menús finales: controles screen, créditos, confirmación salir, high score simple |
| **Assets (6)** | **QA Lead**: Checklist 50+ casos, regression testing, README final, video demo 2 min |

### Checklist QA Final (Integrante 6 lidera, todos participan)

| Categoría | Casos |
|-----------|-------|
| **Core** | Inicio → menú → jugar → pause → resume → menú → salir |
| **Movimiento** | 8 dirs, diagonales contra pared, esquinas, transiciones room |
| **Combate** | Espada hit enemy, enemy hit player, knockback, invulnerabilidad, muerte player, muerte enemy |
| **Pickups** | Corazón cura (max 3), moneda cuenta, llave abre puerta, llave persiste save/load |
| **Enemigos** | Walker patrol/chase, Shooter dispara/evita, Charger charge/stun, Boss 3 fases |
| **Mundo** | 6 rooms completables, puertas llave funcionan, boss room lock/unlock |
| **UI** | HUD correcto siempre, menús navegables teclado+mouse, Game Over/Victoy funcionan |
| **Persistencia** | Save al cambiar room, Load al iniciar, datos correctos |
| **Audio** | SFX todos eventos, música loop, volumen, mute opcional |
| **Performance** | 60 FPS constante, memoria estable 30 min, sin leaks |
| **Build** | .exe corre en PC sin Python, assets incluidos, antivirus no bloquea |

### Entregables Finales
1. **Código** en `main` branch, tag `v1.0.0-entrega`
2. **Build** `dist/ZeldaRPG.exe` (Windows) + `dist/ZeldaRPG` (Linux/Mac si aplica)
3. **Documentación**:
   - `README.md` (cómo jugar, controles, build, créditos)
   - `docs/ANALISIS_Y_DISENO.md`
   - `docs/TAREAS_POR_INTEGRANTE.md`
   - `docs/HITOS_Y_ENTREGAS.md` (este archivo)
   - `docs/REGLAS_EQUIPO.md`
4. **Video demo** 2 min (gameplay + boss fight)
5. **Presentación** 10 min (slides: problema, solución, arquitectura, demo, lecciones)

---

## Buffer de Riesgo (Días 22-28 si hay retrasos)

| Riesgo | Acción de Contingencia |
|--------|------------------------|
| Boss no listo | Simplificar a 2 fases, patrón fijo sin pathfinding |
| Dungeon incompleto | Reducir a 4 rooms lineales, 1 llave |
| Assets faltantes | Usar placeholders coloreados + siluetas claras |
| Save/load roto | Quitar persistencia, solo session actual |
| Performance baja | Reducir partículas, desactivar debug draw, bajar FPS a 30 |
| Integrante ausente | Pair programming + redistribuir tareas "stretch" |

---

## Métricas de Seguimiento (Actualizar cada Daily)

| Métrica | Target | Actual |
|---------|--------|--------|
| % Código en `main` | 100% Día 28 | 0% |
| PRs merged/semana | ≥ 12 (2 c/u) | 0 |
| Bugs críticos abiertos | 0 Día 28 | - |
| Cobertura testing manual | 50 casos Día 28 | 0 |
| Build .exe funcional | Día 26 | No |
| Video demo listo | Día 27 | No |

---

## Comunicación

- **Daily standup:** 15 min, mismo horario, todos los días (presencial/Discord)
- **Weekly retrospective:** Viernes 30 min (qué bien, qué mal, acción mejora)
- **Canal Discord/Slack:** #general, #code-review, #assets, #bugs, #random
- **Issues GitHub:** 1 issue = 1 tarea, labels: `feat`, `bug`, `docs`, `blocked`
- **PR template:** Descripción, cómo testear, screenshots/video, related issues