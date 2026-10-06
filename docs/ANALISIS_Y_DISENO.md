# Documento de Análisis y Diseño - Wave Defense (Python + Pygame)

## 1. Visión General del Juego

**Género:** Arcade Wave Defense / Twin-stick shooter (un solo escenario, oleadas crecientes)  
**Plataforma:** PC (Windows)  
**Motor:** Python 3.10+ + Pygame-ce 2.x  
**Duración estimada:** 10-15 minutos por partida completa (15 oleadas)  
**Equipo:** 6 integrantes | **Tiempo:** 5-6 semanas (hasta 7-14 nov)

---

## 2. Mecánicas Core (MVP)

| Sistema | Descripción | Prioridad |
|---------|-------------|-----------|
| **Movimiento Player** | 8 direcciones (WASD), límites de pantalla, cambio arma (teclas 1-4) | P0 |
| **Sistema de Armas** | 4 armas intercambiables (Strategy Pattern): Pistola, Escopeta, Rifle, Lanzacohetes | P0 |
| **Disparo / Proyectiles** | Click sostenido o tecla, cooldown por arma, hitbox, daño, knockback | P0 |
| **Vidas** | 3 corazones (3 golpes = Game Over), invulnerabilidad 1s tras daño | P0 |
| **Oleadas (Waves)** | Spawner configurado en JSON: tipos, cuenta, HP mult, intervalo spawn | P0 |
| **Enemigos Básicos** | 3 tipos: Basic (estándar), Tank (HP alto, lento), Speedy (rápido, frágil) | P0 |
| **Enemigos Avanzados** | Explosive (muere = explosión área), Splitter (muere = 2 mini) | P1 |
| **Jefes (Boss)** | Oleada 5 y 10: máquina de estados, fases, weak point, telegraphing | P0 |
| **Barreras** | 3-4 colocables, HP visible, reparables (tecla), objetivo prioritario enemigos | P0 |
| **Power-ups** | 4 tipos temporales: velocidad, daño, escudo, slow-mo (spawn aleatorio al matar) | P1 |
| **Tienda Mejoras (Upgrade Shop)** | Entre oleadas: 3 cartas aleatorias (daño, cadencia, vida, velocidad, barrera+) | P0 |
| **Economía** | Oro por matar → gasto en mejoras y reparar barreras | P0 |
| **HUD** | Vidas (3 corazones), ronda, enemigos vivos, oro, arma actual, cooldown visual | P0 |
| **Highscores** | Top 10 persistente en JSON + entrada nombre en Game Over | P1 |
| **Partículas + Juice** | Pool: impacto, muerte, explosión, humo + screen shake + flash daño | P1 |
| **Menús** | Main, Pause, Game Over (input nombre), Victory, Upgrade Shop | P0 |

---

## 3. Arquitectura Técnica

### 3.1 Estructura de Carpetas
```
wave_defense/
├── main.py                    # Entry point, init pygame, Game instance
├── config.py                  # Constantes: WIDTH, HEIGHT, FPS, COLORS, BALANCE
├── core/
│   ├── game.py                # Game loop, StateMachine (MENU, PLAYING, UPGRADE, GAME_OVER, VICTORY)
│   ├── events.py              # EventBus simple (publish/subscribe)
│   └── save_load.py           # JSON: highscores, stats, unlocks
├── entities/
│   ├── entity.py              # Base: pos, vel, rect, hp, alive, update/draw
│   ├── player.py              # Input, movimiento 8-dir, switch arma, invulnerabilidad
│   ├── weapons/               # Strategy Pattern
│   │   ├── weapon.py          # Abstract base: cooldown, damage, spread, projectile_type
│   │   ├── pistol.py
│   │   ├── shotgun.py
│   │   ├── rifle.py
│   │   └── launcher.py
│   ├── projectile.py          # Base proyectil + subclases (bala, perdigón, cohete)
│   ├── enemies/
│   │   ├── enemy.py           # Base: target (base/player), state, path_simple
│   │   ├── basic.py
│   │   ├── tank.py
│   │   ├── speedy.py
│   │   ├── explosive.py
│   │   ├── splitter.py
│   │   └── boss.py            # Fases, patrones, weak point
│   ├── barrier.py             # Sprite con HP, rect, draw_health_bar
│   └── pickup.py              # Power-up temporal (velocidad, daño, escudo, slow-mo)
├── systems/
│   ├── wave_manager.py        # Spawner: oleadas configurables, contador vivos, timer
│   ├── upgrade_shop.py        # Entre oleadas: 3 opciones aleatorias, compra con oro
│   ├── combat.py              # apply_damage, knockback, collide_projectile_enemy
│   └── particles.py           # Pool de partículas: sangre, humo, chispas, screen_shake
├── ui/
│   ├── hud.py                 # Corazones, ronda, enemigos vivos, oro, arma actual
│   ├── menus.py               # MainMenu, PauseMenu, GameOver, Victory
│   └── upgrade_ui.py          # Pantalla 3 cartas: nombre, desc, costo, key para comprar
├── utils/
│   ├── animation.py           # SpriteSheet: frames, duration, loop, flip
│   ├── helpers.py             # clamp, lerp, angle_to, distance, load_spritesheet
│   └── debug.py               # Hitbox toggle, FPS, entity counts
├── config/
│   ├── waves.json             # Definición oleadas 1-15 + bosses
│   └── upgrades.json          # Catálogo mejoras comprables
└── assets/
    ├── sprites/{player,enemies,weapons,barrier,ui,particles}
    ├── sounds/{sfx,music}
    └── fonts/
```

### 3.2 Game Loop & State Machine
```
main.py → Game.init() → Game.run()
  ├─ State.MENU → Menu.handle_events/update/draw
  ├─ State.PLAYING → WaveManager.update + Player.update + Enemies.update + Barriers.update + Particles.update + HUD.draw
  ├─ State.UPGRADE → UpgradeShop.draw + input (1/2/3 para comprar) → auto-vuelve a PLAYING
  ├─ State.PAUSED → Overlay + Menu pausa
  ├─ State.GAME_OVER → Input nombre → save highscore → Menu
  └─ State.VICTORY → Stats finales → highscore → Menu
```

### 3.3 Patrones de Diseño Clave
- **Strategy Pattern**: `Weapon` base + 4 subclases → `Player` cambia arma en runtime
- **Event Bus**: `core/events.py` → desacopla Player, Enemies, Combat, Particles, HUD
- **Object Pool**: `systems/particles.py` → reusa instancias, evita GC
- **Data-Driven**: `waves.json` + `upgrades.json` → balanceo sin tocar código
- **State Machine**: `GameState` enum → transiciones claras, fácil debug

---

## 4. Distribución de Tareas (6 Integrantes)

### Roles y Responsabilidades

| Integrante | Rol Principal | Módulos Responsables | Archivos Clave |
|------------|---------------|----------------------|----------------|
| **1 - Nelson** | **Líder Técnico / Core** | Game loop, State machine, EventBus, Save/Load, Build, Code Review | `main.py`, `config.py`, `core/game.py`, `core/events.py`, `core/save_load.py`, `utils/helpers.py` |
| **2 - Fabiola** | **Player & Weapons System** | Player, Input, Armas (Strategy), Proyectiles, Sistema Combate | `entities/player.py`, `entities/weapons/*.py`, `entities/projectile.py`, `systems/combat.py`, `entities/entity.py` (base) |
| **3 - Lilian** | **Enemies & Wave System** | Enemigos (6 tipos + Boss), WaveManager, Spawning data-driven | `entities/enemies/*.py`, `systems/wave_manager.py`, `config/waves.json` |
| **4 - Zebedeo** | **Barriers, Pickups & Particles** | Barreras (HP, reparar), Power-ups, Particle Pool, Screen Shake, Debug | `entities/barrier.py`, `entities/pickup.py`, `systems/particles.py`, `utils/debug.py` |
| **5 - Aron** | **UI, Upgrades & Menus** | HUD, Menús, Upgrade Shop (data-driven), Highscores, Game Over input | `ui/hud.py`, `ui/menus.py`, `ui/upgrade_ui.py`, `systems/upgrade_shop.py`, `config/upgrades.json` |
| **6 - Leslie** | **Assets & QA Lead** | Sprites, Animaciones, Sonidos, Testing, Bug Tracking, Docs, Video Demo | `assets/` (organizado), `utils/animation.py`, README, checklist QA |

---

## 5. Hitos y Entregas (5-6 Semanas)

| Hito | Fecha Target | Criterios de Aceptación |
|------|--------------|-------------------------|
| **H0: Setup & Core Base** | Fin Semana 1 (12 oct) | Repo clonado, pygame corre 60 FPS, ventana 640×480, State machine MENU↔PLAYING↔PAUSE, EventBus funciona, placeholders assets, git flow + ruff/black |
| **H1: Player + Armas + Enemigos Básicos + Oleadas** | Fin Semana 2 (19 oct) | Player: movimiento 8-dir, switch 4 armas, disparo con cooldown. 3 enemigos básicos funcionales. WaveManager lee JSON y spawnea oleadas 1-5. Colisión proyectil-enemigo → daño → muerte → drop oro. HUD completo. |
| **H2: Barreras + Power-ups + Partículas + Upgrade Shop** | Fin Semana 3 (26 oct) | Barreras colocables/reparables (3-4). 4 power-ups temporales. Particle pool + screen shake. Upgrade Shop entre oleadas: 3 cartas aleatorias desde JSON, compra con oro. Boss oleada 5 funcional. |
| **H3: Contenido Completo + Polish** | Fin Semana 4 (2 nov) | Enemigos Explosive + Splitter. Boss oleada 10 (2 fases). Oleadas 1-15 balanceadas en JSON. Highscores persistentes top 10 + input nombre. Menús completos (main, pause, game over, victory). Assets finales integrados. |
| **H4: Testing + Build + Defensa** | Fin Semana 5 (9 nov) | Checklist 40+ casos probados. 0 bugs críticos. PyInstaller .exe funciona. README + diagrama arquitectura + video 2 min. Cada integrante explica su módulo en 3-5 min. |
| **Buffer / Polish Extra** | Semana 6 (14 nov) | Solo si hace falta: dificultad, edge cases, segunda arena, stats screen. |

---

## 6. Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Scope creep (más armas/enemigos/features) | Alta | Alto | **Feature freeze Semana 3**; todo nuevo = backlog post-entrega |
| Assets no llegan a tiempo | Media | Medio | Placeholders día 1 (rects colores); Leslie entrega assets semanales |
| Merge conflicts en `core/` | Media | Alto | Nelson = owner `core/`; ramas < 3 días; PRs pequeños |
| Un integrante se retrasa | Alta | Alto | Pair programming semanal 1h; micro-tareas reasignables |
| Balancing injugable | Media | Medio | Valores en `config.py` + `waves.json`; playtest interno viernes |
| No llegan a ~1000 líneas | Baja | Medio | Si falta: más upgrades, partículas, stats screen, arena 2 |

---

## 7. Decisiones Técnicas Confirmadas

1. **Tilemap/Mapa:** No hay. Un solo escenario fijo (640×480), barreras colocables en posiciones fijas o grid simple.
2. **Resolución:** Fija 640×480 surface interna → escalar si needed (pixel perfect).
3. **Sprites:** Assets propios (Leslie). Placeholders día 1. Paleta definida semana 1.
4. **Sonidos:** sfxr/bfxr para SFX + música libre (opengameart/itch.io).
5. **Build final:** PyInstaller one-file Windows (`.exe`).
6. **Control:** WASD movimiento + Mouse aim (click izq disparo) + Teclas 1-4 cambio arma.
7. **Python:** 3.10+ (match/case en state machine, type hints obligatorios).

---

## 8. Próximos Pasos Inmediatos (Semana 1 - Esta semana)

1. **Nelson**: Crear repo + `.gitignore` + `requirements.txt` + README base + `config.py` + `main.py` + `core/game.py` (state machine) + `core/events.py` (EventBus) + `core/save_load.py` (esqueleto) + `utils/helpers.py`
2. **Todos**: Configurar `ruff` + `black` + pre-commit hook
3. **Leslie**: Placeholders TODOS sprites (rectángulos colores con nombres correctos en `assets/sprites/`)
4. **Fabiola**: `entities/entity.py` + `entities/player.py` (movimiento 8-dir, switch arma 1-4, invulnerabilidad)
5. **Lilian**: `entities/enemies/enemy.py` + `entities/enemies/basic.py` + `config/waves.json` (oleadas 1-5)
6. **Aron**: `ui/hud.py` (vidas, ronda, oro, arma, enemigos vivos)
7. **Zebedeo**: `entities/barrier.py` (esqueleto HP + draw) + `systems/particles.py` (pool base)
8. **Viernes**: **Sync 30 min** → Demo: menú→playing→pause, player se mueve/cambia arma, HUD muestra estado, 1 enemigo básico spawnea y muere al dispararle.