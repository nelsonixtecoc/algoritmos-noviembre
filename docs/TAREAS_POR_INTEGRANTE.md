# Tareas por Integrante - Wave Defense

## Asignación de Roles (6 Integrantes)

| # | Integrante | Rol | Módulos Responsables | Archivos Clave |
|---|------------|-----|----------------------|----------------|
| 1 | **Nelson** | Líder Técnico / Core | Game loop, State machine, EventBus, Save/Load, Build, Code Review | `main.py`, `config.py`, `core/game.py`, `core/events.py`, `core/save_load.py`, `utils/helpers.py` |
| 2 | **Fabiola** | Player & Weapons System | Player, Input, Armas (Strategy), Proyectiles, Sistema Combate | `entities/player.py`, `entities/weapons/*.py`, `entities/projectile.py`, `systems/combat.py`, `entities/entity.py` |
| 3 | **Lilian** | Enemies & Wave System | Enemigos (6 tipos + Boss), WaveManager, Spawning data-driven | `entities/enemies/*.py`, `systems/wave_manager.py`, `config/waves.json` |
| 4 | **Zebedeo** | Barriers, Pickups & Particles | Barreras (HP, reparar), Power-ups, Particle Pool, Screen Shake, Debug | `entities/barrier.py`, `entities/pickup.py`, `systems/particles.py`, `utils/debug.py` |
| 5 | **Aron** | UI, Upgrades & Menus | HUD, Menús, Upgrade Shop (data-driven), Highscores, Game Over input | `ui/hud.py`, `ui/menus.py`, `ui/upgrade_ui.py`, `systems/upgrade_shop.py`, `config/upgrades.json` |
| 6 | **Leslie** | Assets & QA Lead | Sprites, Animaciones, Sonidos, Testing, Bug Tracking, Docs, Video Demo | `assets/`, `utils/animation.py`, README, checklist QA |

---

## Desglose Detallado por Integrante

### 🎯 Integrante 1 - Nelson (Líder Técnico / Core)

**Semana 1:**
- [ ] `main.py` - Entry point, init pygame, instancia Game, bucle principal
- [ ] `config.py` - Constantes: WIDTH, HEIGHT, FPS, COLORS, LAYERS, BALANCE (velocidad player, daño base, etc.)
- [ ] `core/game.py` - Clase Game, StateMachine (MENU, PLAYING, UPGRADE, PAUSED, GAME_OVER, VICTORY), transiciones
- [ ] `core/events.py` - EventBus: subscribe, publish, process (colisiones, daño, muerte, pickup, wave_complete)
- [ ] `core/save_load.py` - JSON: highscores (top 10), stats totales, unlocks
- [ ] `utils/helpers.py` - clamp, lerp, angle_to, distance, load_spritesheet, random_spawn_point
- [ ] Setup repo: `.gitignore`, `requirements.txt` (pygame-ce), README inicial, pre-commit (ruff + black)

**Semana 2-3:**
- [ ] Integración continua: mergear PRs, resolver conflictos, builds semanales
- [ ] Code review de todos los PRs (mínimo 1 aprobación)
- [ ] Ajustar `config.py` tras playtests (balanceo)

**Semana 4-5:**
- [ ] Build final con PyInstaller (--onefile --noconsole --add-data assets)
- [ ] Documentación técnica final: arquitectura, patrones usados, decisiones
- [ ] Preparar material defensa oral: diagrama flujo game loop + event bus

---

### ⚔️ Integrante 2 - Fabiola (Player & Weapons System)

**Semana 1:**
- [ ] `entities/entity.py` - Clase base: pos (Vector2), vel, rect, hp, max_hp, alive, sprite, animation, update(dt), draw(surface, camera_offset)
- [ ] `entities/player.py` - Hereda Entity: input WASD (8 dirs), límites pantalla, switch arma (teclas 1-4), invulnerabilidad 1s (flash), hp=3, oro=0
- [ ] `entities/weapons/weapon.py` - Abstract base: cooldown, damage, spread, projectile_class, fire(pos, angle) → devuelve lista Projectile

**Semana 2:**
- [ ] `entities/weapons/pistol.py` - 1 bala, cooldown 300ms, daño 10, spread 0°
- [ ] `entities/weapons/shotgun.py` - 5 perdigones, cooldown 800ms, daño 6 c/u, spread ±15°
- [ ] `entities/weapons/rifle.py` - 1 bala rápida, cooldown 150ms, daño 8, spread 0°, perfora 1 enemigo
- [ ] `entities/weapons/launcher.py` - 1 cohete, cooldown 1500ms, daño 40, explosión radio 60px al impactar
- [ ] `entities/projectile.py` - Base: pos, vel, damage, owner, lifetime, pierce, explode_on_death, update(dt), draw()
- [ ] `systems/combat.py` - `apply_damage(attacker, target, amount, knockback)`, `check_projectile_collisions(projectiles, enemies)`, `check_player_enemy_collision(player, enemies)`

**Semana 3:**
- [ ] Stats player: damage_mult, cooldown_mult, speed_mult, max_hp (modificables por upgrades)
- [ ] Knockback al recibir daño + invulnerabilidad flash
- [ ] Pickup oro al matar (EventBus: ENEMY_KILLED → Player.add_gold)

**Semana 4:**
- [ ] Balanceo: valores finales en `config.py`
- [ ] Testing edge cases: esquinas, disparo diagonal, cambio arma mid-cooldown

---

### 👹 Integrante 3 - Lilian (Enemies & Wave System)

**Semana 1:**
- [ ] `entities/enemies/enemy.py` - Base Enemy: target (base o player), state (IDLE, CHASE, ATTACK), speed, hp, damage, gold_value, update(dt), simple_pathfinding (vector directo evitando barreras básico)
- [ ] `entities/enemies/basic.py` - Standard: hp 30, speed 80, damage 1, gold 10
- [ ] `entities/enemies/tank.py` - HP 120, speed 40, damage 2, gold 25, resist knockback 50%
- [ ] `entities/enemies/speedy.py` - HP 15, speed 180, damage 1, gold 15, dodge chance 10%

**Semana 2:**
- [ ] `systems/wave_manager.py` - Lee `config/waves.json`, spawnea oleadas, timer entre oleadas, contador enemigos vivos, evento WAVE_COMPLETE
- [ ] `config/waves.json` - Oleadas 1-15: tipos, count, hp_mult, spawn_interval, boss cada 5
- [ ] Integración WaveManager → Game.playing: spawnea en bordes pantalla (top/bottom/left/right aleatorio)

**Semana 3:**
- [ ] `entities/enemies/explosive.py` - HP 25, speed 100, al morir: explosión radio 80px, daño 20 a player/barreras/enemigos
- [ ] `entities/enemies/splitter.py` - HP 40, speed 60, al morir: spawnea 2 `mini_splitter` (hp 10, speed 120, damage 1)
- [ ] `entities/enemies/boss.py` - Boss oleada 5: 3 fases, hp 500→300→200, patrones: radial burst, charge, summon basics. Weak point: brilla 3s cada fase.

**Semana 4:**
- [ ] Boss oleada 10: 2 fases, hp 800→400, patrones: laser telegraph, homing missiles, arena shrink
- [ ] Tuning dificultad: HP, daño, timings por oleada en `waves.json`
- [ ] Death animations + drop oro + partículas (EventBus)

---

### 🧱 Integrante 4 - Zebedeo (Barriers, Pickups & Particles)

**Semana 1:**
- [ ] `entities/barrier.py` - Sprite con HP (max 200), rect, draw_health_bar(), take_damage(), repair(amount), can_place(pos) → grid snap 40px
- [ ] Placeholders: 4 posiciones fijas defensa base (esquinas zona player)

**Semana 2:**
- [ ] Barreras colocables: tecla B → ghost preview → click confirma (costa 50 oro)
- [ ] Reparar: tecla R cerca barrera → gasta 10 oro/s → repara 20 HP/s
- [ ] Enemigos priorizan barreras si en rango → atacan → si destruida, van a player/base

**Semana 3:**
- [ ] `entities/pickup.py` - Base: tipo (SPEED, DAMAGE, SHIELD, SLOWMO), duration, effect(), spawn_random_on_kill(chance=15%)
- [ ] Power-ups: Speed (1.5x vel 5s), Damage (2x dmg 5s), Shield (inmune 3s), SlowMo (0.5x time 4s)
- [ ] `systems/particles.py` - Pool: crea 200 partículas al inicio. Tipos: `Impact` (chispas), `Death` (humo), `Explosion` (anillos), `Blood` (gotas). `screen_shake(intensity, duration)`
- [ ] `utils/debug.py` - Toggle hitboxes (F3), FPS counter, entity counts, wave info

**Semana 4:**
- [ ] Polish partículas: color por tipo enemigo, fade out, gravity
- [ ] Screen shake en: player hit, boss hit, explosiones, wave complete
- [ ] Testing visual: claridad feedback, no spam partículas

---

### 🖥️ Integrante 5 - Aron (UI, Upgrades & Menus)

**Semana 1:**
- [ ] `ui/hud.py` - 3 corazones (sprites full/half/empty), ronda (wave 1/15), enemigos vivos, oro, icono arma actual + cooldown bar
- [ ] Fuente pixel art cargada desde `assets/fonts/`

**Semana 2:**
- [ ] `ui/menus.py` - MainMenu (Jugar, Controles, Highscores, Salir), PauseMenu (Continuar, Reiniciar, Menú Principal, Salir)
- [ ] `ui/game_over.py` - Pantalla Game Over + input nombre (máx 12 chars, solo alfanumérico) → save highscore → volver a menú
- [ ] `ui/victory.py` - Pantalla victoria: tiempo, oleadas completadas, oro total, accuracy, highscores

**Semana 3:**
- [ ] `systems/upgrade_shop.py` - Carga `config/upgrades.json`, elige 3 aleatorias (sin repetir), aplica efecto al comprar
- [ ] `config/upgrades.json` - 12-15 upgrades: daño, cadencia, vida max, velocidad, barrera HP, barrera regen, oro extra, pierce, spread, etc.
- [ ] `ui/upgrade_ui.py` - 3 cartas centradas: nombre, descripción, costo, tecla (1/2/3), hover highlight, confirmación
- [ ] Integración sonidos: `assets/sounds/` (sfx: shoot, hit, kill, coin, upgrade, wave_start, game_over + música loop 2 tracks)

**Semana 4:**
- [ ] Polish: transiciones fade in/out entre estados, screen shake en menús
- [ ] Highscores: top 10 persistente, muestra en MainMenu y Game Over
- [ ] Testing UX: legibilidad, navegación teclado/mouse, controles intuitivos

---

### 🎨 Integrante 6 - Leslie (Assets & QA Lead)

**Semana 1 (continuo):**
- [ ] Estructura `assets/`:
  ```
  assets/
  ├── sprites/
  │   ├── player/        # idle.png, walk_1-4.png, shoot.png, hurt.png (por arma)
  │   ├── enemies/       # basic/, tank/, speedy/, explosive/, splitter/, boss/
  │   ├── weapons/       # pistol.png, shotgun.png, rifle.png, launcher.png, projectiles/
  │   ├── barrier/       # barrier_1-4.png, barrier_destroyed.png
  │   ├── ui/            # heart_full.png, heart_empty.png, coin.png, upgrade_cards/
  │   └── particles/     # spark.png, smoke.png, ring.png, blood.png
  ├── sounds/
  │   ├── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, explode, hurt)
  │   └── music/         # main_loop.ogg, boss_loop.ogg
  └── fonts/             # .ttf pixel art (ej. PressStart2P, Pixeloid)
  ```
- [ ] Placeholders día 1: rectángulos colores para TODOS sprites (permite trabajar al resto)

**Semana 2-3:**
- [ ] Sprites finales progresivos (prioridad: player → enemigos básicos → armas/proyectiles → barreras → boss → UI → partículas)
- [ ] `utils/animation.py` - Clase Animation: frames (list[Surface]), duration, loop, flip_h, flip_v, get_frame(dt)
- [ ] Sonidos generados con sfxr/bfxr + música libre (opengameart/itch.io)

**Semana 4 (QA intensivo):**
- [ ] Testing manual completo: checklist 40+ casos (ver abajo)
- [ ] Bug tracking: GitHub Issues con labels (bug/critical, bug/minor, feature, balance)
- [ ] Regression testing tras cada merge
- [ ] README final: controles, cómo jugar, arquitectura, patrones, créditos, build instructions
- [ ] Video/demo gameplay 2 min para entrega (OBS, 60 FPS)

**Semana 5:**
- [ ] Pre-defensa: cada integrante ensaya explicar su módulo (3-5 min)
- [ ] Checklist final: 0 bugs críticos, build funciona en PC limpio, docs completas

---

## Matriz de Dependencias Críticas (¡Leer antes de empezar!)

| Módulo | Requiere antes | Bloquea a | Semana objetivo |
|--------|----------------|-----------|-----------------|
| `config.py` | — | Todos | 1 |
| `core/events.py` | `config.py` | Player, Enemies, Combat, Particles, WaveManager | 1 |
| `core/game.py` | `events.py`, `config.py` | Todos | 1 |
| `entities/entity.py` | `config.py`, `events.py` | Player, Enemy, Projectile, Barrier, Pickup | 1 |
| `entities/player.py` | `entity.py`, `weapons/weapon.py` | Combat, HUD, Upgrades | 1-2 |
| `entities/weapons/weapon.py` + 4 armas | `entity.py`, `projectile.py` | Player, Combat | 2 |
| `entities/projectile.py` | `entity.py` | Weapons, Combat | 2 |
| `entities/enemies/enemy.py` | `entity.py` | Todos enemigos, WaveManager | 1-2 |
| `systems/wave_manager.py` | `enemies/`, `config/waves.json` | Game loop playing | 2 |
| `systems/combat.py` | `player.py`, `enemies/`, `projectile.py` | — | 2 |
| `entities/barrier.py` | `entity.py` | Player (reparar), WaveManager (target), Enemies (target) | 2-3 |
| `systems/particles.py` | `events.py` | Todos (feedback visual) | 3 |
| `entities/pickup.py` | `entity.py`, `events.py` | WaveManager (spawn on kill) | 3 |
| `systems/upgrade_shop.py` + `ui/upgrade_ui.py` | `player.py`, `config/upgrades.json` | Game state UPGRADE | 3 |
| `entities/boss.py` | `enemy.py`, `particles.py` | Wave 5, 10 | 3-4 |
| `core/save_load.py` | `config.py` | Highscores, Game Over, Victory | 4 |
| `ui/menus.py` + `ui/game_over.py` | `save_load.py` | — | 4 |

**Regla de oro:** Si tu módulo está en "Bloquea a", prioriza terminarlo. Si está en "Requiere antes", avisa al dueño cuando lo necesites.

---

## Checklist de Entrega por Integrante (Definición de "Done")

- [ ] Código en `main` via PR aprobado (1+ review)
- [ ] Sin warnings `ruff` / `flake8` / `mypy` (si config)
- [ ] Funciona en 640×480
- [ ] Probado con placeholders Y assets finales
- [ ] Documentado en README o docstrings públicas
- [ ] Commits atómicos y mensajes claros (`feat:`, `fix:`, `refactor:`)
- [ ] **Puede explicar su módulo en 3-5 min** (diagrama + código clave + bug resuelto)

---

## Checklist QA (Leslie - Semana 4-5)

### Funcionalidad Core
- [ ] Menú → Jugar → Playing → Pause → Continuar funciona
- [ ] Player: movimiento 8 dirs, límites, switch 4 armas, disparo, cooldown
- [ ] 3 vidas: pierde 1 al tocar enemigo, invulnerabilidad 1s, Game Over en 0
- [ ] Oleadas 1-15: spawnean correctamente, contador enemigos vivos baja al matar
- [ ] Wave 5 y 10: Boss aparece, fases funcionan, weak point vulnerable
- [ ] Enemigos: 6 tipos comportamientos distintos, mueren, dan oro
- [ ] Barreras: colocar, reparar, enemigos las atacan, HP visible
- [ ] Power-ups: spawnean al matar, aplican efecto temporal, icono HUD
- [ ] Upgrade Shop: aparece entre oleadas, 3 cartas, compra gasta oro, efecto aplicado
- [ ] Highscores: guarda top 10, input nombre Game Over, muestra en menú
- [ ] Victoria: oleada 15 completada → pantalla victoria → highscore

### Visual / Audio
- [ ] Assets finales integrados (no placeholders)
- [ ] Partículas: impacto, muerte, explosión, screen shake
- [ ] Animaciones fluidas (player, enemigos, boss)
- [ ] Sonidos: disparo, impacto, muerte, moneda, upgrade, ola, música
- [ ] HUD legible: vidas, ronda, oro, arma, cooldown, enemigos

### Técnico
- [ ] 60 FPS estables (sin drops >5 frames)
- [ ] Sin memory leaks (particle pool reusa, no crea inf)
- [ ] Build .exe funciona en PC sin Python
- [ ] Git history limpio (commits atómicos, mensajes claros)

### Documentación
- [ ] README completo
- [ ] Diagrama arquitectura (draw.io / papel foto)
- [ ] Video 2 min gameplay