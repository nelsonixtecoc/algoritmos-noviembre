# Hitos y Entregas - Wave Defense (5-6 Semanas)

## Cronograma General

| Semana | Fechas | Hito | Entregable Principal |
|--------|--------|------|----------------------|
| **1** | 6-12 Oct | **H0: Setup & Core Base** | Juego arranca, state machine, event bus, placeholders, git flow |
| **2** | 13-19 Oct | **H1: Gameplay Core** | Player + 4 armas + 3 enemigos + oleadas 1-5 + HUD + colisiones |
| **3** | 20-26 Oct | **H2: Systems Completion** | Barreras, power-ups, partículas, upgrade shop, boss wave 5 |
| **4** | 27 Oct - 2 Nov | **H3: Content Complete** | Todos enemigos, boss wave 10, oleadas 1-15, highscores, menús, assets finales |
| **5** | 3-9 Nov | **H4: Polish & Defense** | Testing 40+, build .exe, docs, video, ensayo defensa oral |
| **6** | 10-14 Nov | **Buffer (opcional)** | Solo si hace falta: dificultad, 2ª arena, stats screen, polish extra |

---

## Detalle por Hito

### H0: Setup & Core Base (Semana 1 - 6-12 Oct)
**Objetivo:** Infraestructura lista para que todos trabajen en paralelo sin bloqueos.

| Tarea | Responsable | Criterio Done |
|-------|-------------|---------------|
| Repo + .gitignore + requirements.txt + README | Nelson | `git clone` → `pip install -r requirements.txt` → `python main.py` abre ventana 640×480 60 FPS |
| `config.py` con constantes base | Nelson | WIDTH, HEIGHT, FPS, COLORS, PLAYER_SPEED, PLAYER_HP, etc. |
| `core/game.py` StateMachine completa | Nelson | MENU → PLAYING → PAUSE → GAME_OVER → VICTORY → MENU (teclas funcionan) |
| `core/events.py` EventBus funcional | Nelson | `bus.subscribe("TEST", fn)`, `bus.publish("TEST", data)` → fn recibe data |
| `core/save_load.py` esqueleto | Nelson | `save_highscore(name, score)`, `load_highscores()` → lista dicts |
| `utils/helpers.py` funciones base | Nelson | clamp, lerp, angle_to, distance, load_spritesheet probadas |
| Placeholders TODOS sprites | Leslie | `assets/sprites/` con rects colores nombrados: player_idle.png, enemy_basic.png, etc. |
| Pre-commit: ruff + black | Nelson | `git commit` formatea y lintea automático |
| Convención código acordada | Todos | type hints, snake_case, docstrings mínimas, commits `feat:`/`fix:` |

**Demo viernes 12 oct (30 min sync):**
- Menú principal navega teclas ↑↓ + Enter
- Enter → Playing → Player rectángulo se mueve WASD (8 dirs)
- Teclas 1-4 cambian "arma" (cambia color rectángulo)
- Espacio → "dispara" (print consola)
- Escape → Pause → Escape → Playing
- F3 → toggle hitboxes (debug)

---

### H1: Gameplay Core (Semana 2 - 13-19 Oct)
**Objetivo:** Loop jugable completo: player dispara → enemigos mueren → dan oro → siguiente ola.

| Tarea | Responsable | Criterio Done |
|-------|-------------|---------------|
| `entities/entity.py` base completa | Fabiola | pos, vel, rect, hp, alive, update/draw, take_damage, knockback |
| `entities/player.py` movimiento + switch arma | Fabiola | WASD 8 dirs, límites pantalla, 1-4 cambia arma, invuln 1s flash |
| 4 armas Strategy Pattern | Fabiola | Pistola, Escopeta, Rifle, Lanzacohetes → feel distinto (cadencia, spread, daño) |
| `entities/projectile.py` + subclases | Fabiola | Bala, perdigón, cohete (explota), lifetime, pierce |
| `systems/combat.py` colisiones | Fabiola | Proyectil choca enemigo → daño → knockback → muerte → EventBus ENEMY_KILLED |
| 3 enemigos básicos | Lilian | Basic, Tank, Speedy → spawnean, persiguen player/base, atacan, mueren, dan oro |
| `systems/wave_manager.py` + `waves.json` | Lilian | Lee JSON, spawnea oleadas 1-5, timer 5s entre oleadas, contador vivos en HUD |
| `ui/hud.py` completo | Aron | 3 corazones, ronda (1/15), enemigos vivos, oro, arma actual + cooldown bar |
| Integración Player → WaveManager → HUD | Todos | Jugar 5 oleadas sin crashear, oro sube, vidas bajan, Game Over funciona |

**Demo viernes 19 oct:**
- Partida completa oleadas 1-5
- 4 armas se sienten distintas
- 3 enemigos comportamientos visibles
- HUD muestra todo correctamente
- Game Over → input nombre → highscore → menú

---

### H2: Systems Completion (Semana 3 - 20-26 Oct)
**Objetivo:** Sistemas de profundidad: barreras, power-ups, partículas, upgrades, primer boss.

| Tarea | Responsable | Criterio Done |
|-------|-------------|---------------|
| `entities/barrier.py` colocar/reparar | Zebedeo | Tecla B ghost preview, click coloca (50 oro), tecla R repara (10 oro/s) |
| Enemigos atacan barreras prioritarias | Lilian + Zebedeo | Si barrera en rango → ataca barrera → si no, player/base |
| 4 power-ups temporales | Zebedeo | Speed, Damage, Shield, SlowMo → spawn 15% al matar, duración 3-5s, icono HUD |
| `systems/particles.py` pool + screen shake | Zebedeo | 200 partículas pre-creadas, tipos: impact, death, explosion, blood. Shake en hit/boss/explosion |
| `config/upgrades.json` 12-15 upgrades | Aron | Daño, cadencia, vida, velocidad, barrera HP, oro extra, pierce, spread, etc. |
| `systems/upgrade_shop.py` + `ui/upgrade_ui.py` | Aron | Entre oleadas: 3 cartas aleatorias, teclas 1/2/3 compran, efecto inmediato |
| Boss oleada 5 (3 fases) | Lilian | HP 500, patrones: radial burst, charge, summon basics. Weak point brilla 3s/fase |
| `utils/debug.py` | Zebedeo | F3 hitboxes, FPS, entity counts, wave info |
| Assets week 1-2 integrados | Leslie | Player animado, 3 enemigos básicos, proyectiles, barrera, UI básica |

**Demo viernes 26 oct:**
- Barreras se colocan/reparan, enemigos las destruyen
- Power-ups spawnean y funcionan
- Partículas en cada impacto/muerte + screen shake
- Upgrade Shop aparece oleada 2, 3, 4... compra funciona
- Boss oleada 5 se vence (3 fases)

---

### H3: Content Complete (Semana 4 - 27 Oct - 2 Nov)
**Objetivo:** Juego completo contenido + assets finales + menús pulidos.

| Tarea | Responsable | Criterio Done |
|-------|-------------|---------------|
| Enemigo Explosive + Splitter | Lilian | Explosive: muerte = explosión área. Splitter: muerte = 2 mini |
| Boss oleada 10 (2 fases) | Lilian | HP 800, laser telegraph, homing missiles, arena shrink |
| `waves.json` oleadas 1-15 balanceadas | Lilian | Dificultad curva suave, variety tipos, oro escalado |
| `core/save_load.py` highscores completos | Nelson | Top 10 persistente JSON, carga en MainMenu y GameOver |
| `ui/menus.py` + `ui/game_over.py` + `ui/victory.py` | Aron | Main, Pause, Game Over (input nombre), Victory (stats), Highscores screen |
| Sonidos + música integrados | Leslie + Aron | SFX: shoot, hit, kill, coin, upgrade, wave, explode, hurt. Música: main + boss loop |
| Assets finales TODOS integrados | Leslie | 0 placeholders. Spritesheets animados, UI consistente, partículas con sprites |
| Balanceo final playtesting | Todos | 3-4 partidas completas ajustando `config.py` + `waves.json` + `upgrades.json` |

**Demo viernes 2 nov:**
- Partida completa 1-15 oleadas + victoria
- Todos los enemigos + bosses funcionales
- Menús navegables teclado + mouse
- Highscores guardan y muestran
- Assets finales, sonidos, música
- 0 crashes, 60 FPS

---

### H4: Polish & Defense (Semana 5 - 3-9 Nov)
**Objetivo:** Calidad de entrega + preparación defensa oral.

| Tarea | Responsable | Criterio Done |
|-------|-------------|---------------|
| Checklist QA 40+ casos | Leslie | Ver `TAREAS_POR_INTEGRANTE.md` → sección Checklist QA |
| Bugfix regression (0 críticos) | Todos | Issues GitHub cerrados, re-test tras cada fix |
| PyInstaller build .exe | Nelson | `dist/game.exe` funciona en PC sin Python, assets incluidos |
| README final | Leslie | Controles, cómo jugar, arquitectura, patrones, créditos, build |
| Video gameplay 2 min | Leslie | OBS 60 FPS, muestra: menú, gameplay oleadas 1-3, boss 5, upgrade shop, victoria |
| Docs defensa oral | Cada uno | Diagrama flujo módulo (papel/draw.io), 2 capturas código clave, 1 bug difícil resuelto |
| Ensayo defensa grupal | Todos | Cada uno explica 3-5 min, preguntas cruzadas, tiempo total < 30 min |

**Entrega final viernes 9 nov (o 14 nov si buffer):**
- Repo tag `v1.0-entrega`
- `.exe` en `dist/` o release GitHub
- README + video + diagramas en `/docs/defensa/`

---

### Buffer Semana 6 (10-14 Nov) - Solo si hace falta
| Opcional | Responsable | Notas |
|----------|-------------|-------|
| Segunda arena (layout distinto) | Lilian + Zebedeo | `config/arenas.json`, selector en menú |
| Stats screen post-partida | Aron | Accuracy, tiempo, kills por tipo, upgrades comprados |
| Dificultad ajustable (Fácil/Normal/Difícil) | Nelson | Multiplicadores en `config.py` |
| Polish visual extra | Leslie | Partículas únicas por arma, trails, shaders simples |
| Bugs edge cases | Todos | Esquinas, spawns raros, memory leaks |

---

## Matriz de Responsabilidad por Hito

| Módulo / Feature | H0 | H1 | H2 | H3 | H4 | Owner |
|------------------|----|----|----|----|----|-------|
| Repo / Config / Build | ✅ | | | | ✅ | Nelson |
| Game Loop / State Machine | ✅ | | | | | Nelson |
| EventBus | ✅ | | | | | Nelson |
| Save/Load Highscores | | | | ✅ | | Nelson |
| Entity Base | | ✅ | | | | Fabiola |
| Player + Movimiento | | ✅ | | | | Fabiola |
| Armas (4) + Proyectiles | | ✅ | | | | Fabiola |
| Combate / Colisiones | | ✅ | | | | Fabiola |
| Enemigos Base + 3 Básicos | | ✅ | | | | Lilian |
| WaveManager + waves.json | | ✅ | ✅ | ✅ | | Lilian |
| Enemigos Avanzados (2) | | | ✅ | | | Lilian |
| Boss Wave 5 + 10 | | | ✅ | ✅ | | Lilian |
| Barreras | | | ✅ | | | Zebedeo |
| Power-ups | | | ✅ | | | Zebedeo |
| Partículas + Screen Shake | | | ✅ | | | Zebedeo |
| Debug Tools | | | ✅ | | | Zebedeo |
| HUD | | ✅ | | | | Aron |
| Menús (Main, Pause, GO, Victory) | | | | ✅ | | Aron |
| Upgrade Shop + upgrades.json | | | ✅ | | | Aron |
| Sonidos + Música | | | | ✅ | | Leslie + Aron |
| Assets (sprites, animaciones) | ✅ placeholders | | | ✅ finales | | Leslie |
| Animation System | | | | ✅ | | Leslie |
| QA / Testing / Bug Tracking | | | | ✅ | ✅ | Leslie |
| README / Video / Docs Defensa | | | | | ✅ | Leslie |

---

## Criterios de Aceptación Globales (Para la nota)

### Técnicos (40%)
- [ ] Arquitectura modular, patrones aplicados correctamente (Strategy, EventBus, Pool, StateMachine, Data-Driven)
- [ ] Código limpio: type hints, naming, docstrings, sin warnings linter
- [ ] Git history significativo: commits atómicos, PRs revisados, ramas cortas
- [ ] Build funcional .exe + assets embebidos
- [ ] 60 FPS estables, sin memory leaks, sin crashes

### Jugabilidad (30%)
- [ ] Loop completo 15 oleadas jugable y divertido
- [ ] 4 armas se sienten distintas y útiles
- [ ] 6 enemigos + 2 bosses con comportamientos claros
- [ ] Progresión: oro → upgrades → poder visible
- [ ] Dificultad justa (balanceado en config/JSON)

### Presentación (20%)
- [ ] Assets propios coherentes (estilo pixel art unificado)
- [ ] Juice: partículas, screen shake, flash, sonidos, feedback claro
- [ ] UI/UX: menús navegables, HUD legible, upgrade shop entendible
- [ ] Video 2 min muestra features clave

### Defensa Oral (10%)
- [ ] Cada integrante explica su módulo 3-5 min con diagrama + código
- [ ] Responden preguntas: "¿Por qué este patrón?", "¿Cómo debuggeaste X?", "¿Qué cambiarías?"
- [ ] Equipo demuestra comprensión compartida (no solo dueño del módulo)

---

## Fechas Clave Recordatorio

| Evento | Fecha |
|--------|-------|
| Inicio proyecto | 6 Oct (Lunes) |
| H0 Demo | 12 Oct (Sábado) |
| H1 Demo | 19 Oct (Sábado) |
| H2 Demo | 26 Oct (Sábado) |
| H3 Demo | 2 Nov (Sábado) |
| **Entrega final (H4)** | **9 Nov (Sábado)** |
| Buffer opcional | 14 Nov (Sábado) |
| Defensa oral (estimada) | Semana 10-14 Nov |

> **Nota:** Los sábados son syncs obligatorios 30 min. Si alguien no puede, avisa miércoles previo para redistribuir.