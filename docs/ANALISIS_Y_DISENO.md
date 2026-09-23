# Documento de Análisis y Diseño - RPG Estilo Zelda (Python + Pygame)

## 1. Visión General del Juego

**Género:** Action-RPG top-down (estilo Zelda clásico: Link to the Past, Link's Awakening)  
**Plataforma:** PC (Windows/Linux/Mac)  
**Motor:** Python 3.10+ + Pygame 2.x  
**Duración estimada:** 15-20 minutos de gameplay  
**Equipo:** 6 integrantes | **Tiempo:** 4 semanas

---

## 2. Mecánicas Core (MVP)

| Sistema | Descripción | Prioridad |
|---------|-------------|-----------|
| **Movimiento** | 8 direcciones, tile-based o pixel-perfect, colisiones con paredes/obstáculos | P0 |
| **Combate** | Espada (melee), proyectiles opcionales, invulnerabilidad temporal tras daño | P0 |
| **Vidas/HP** | 3 corazones (3 golpes = game over), pickups de corazón | P0 |
| **Monedas (Rupias)** | Drop de enemigos/coffres, contador HUD, sin uso en MVP (solo score) | P0 |
| **Enemigos** | 3 tipos: caminante, disparador, cargador; IA simple (patrulla/persecución) | P0 |
| **Jefe Final** | 2-3 fases, patrones de ataque distintos, arena dedicada | P0 |
| **Progresión** | Llaves → abre puertas → nuevas áreas → jefe | P0 |
| **Game Over** | Pierde todas las vidas → pantalla Game Over → reinicio desde inicio | P0 |
| **Niveles/EXP** | Opcional MVP: solo HP fijo; si tiempo permite: subir nivel = +1 corazón max | P1 |
| **Inventario** | Opcional: solo llaves y contador monedas | P1 |

---

## 3. Arquitectura Técnica

### 3.1 Estructura de Carpetas
```
zelda_rpg/
├── main.py                    # Entry point, inicialización
├── config.py                  # Constantes globales (WIDTH, HEIGHT, FPS, TILE_SIZE, COLORS)
├── assets/                    # Sprites, sonidos, fuentes (organizados en subcarpetas)
│   ├── sprites/
│   │   ├── player/
│   │   ├── enemies/
│   │   ├── tiles/
│   │   └── ui/
│   ├── sounds/
│   └── fonts/
├── core/
│   ├── game.py                # Game loop, state machine (MENU, PLAYING, PAUSED, GAME_OVER, VICTORY)
│   ├── events.py              # Event bus / colisiones globales
│   ├── save_load.py           # JSON save/load (checkpoint o inicio)
│   └── camera.py              # Cámara que sigue al jugador
├── entities/
│   ├── entity.py              # Clase base: pos, rect, sprite, hp, alive, update/draw
│   ├── player.py              # Input, movimiento, ataque, invulnerabilidad, stats
│   ├── enemy.py               # Clase base enemigo + IA (patrulla, chase, attack)
│   ├── enemies/               # Subclases: Walker, Shooter, Charger
│   ├── boss.py                # Jefe final con máquina de estados (fases)
│   ├── projectile.py          # Flechas, bolas de fuego, espada hitbox
│   └── pickup.py              # Corazón, moneda, llave
├── world/
│   ├── tilemap.py             # Carga CSV/TMX, render, colisiones por capa
│   ├── room.py                # Habitación individual: enemies, pickups, doors, triggers
│   ├── dungeon.py             # Grafo de habitaciones, transiciones, llaves/puertas
│   └── level_data/            # Archivos de mapa (CSV o JSON)
├── systems/
│   ├── combat.py              # Resolución daño, knockback, invulnerabilidad
│   ├── inventory.py           # Llaves, monedas, items clave
│   ├── leveling.py            # (P1) EXP, level up, stat upgrades
│   └── pathfinding.py         # A* simple para enemigos que persiguen
├── ui/
│   ├── hud.py                 # Corazones, monedas, llaves, minimapa opcional
│   ├── menus.py               # Main menu, pause, game over, victory
│   └── dialogue.py            # (P1) Texto NPCs, tutorial
└── utils/
    ├── helpers.py             # Distancia, clamping, load_sprite_sheet
    ├── animation.py           # Manejo de spritesheets y animaciones
    └── debug.py               # Hitbox toggle, FPS counter
```

### 3.2 Game Loop & State Machine
```
main.py → Game.init() → Game.run()
  ├─ State.MENU → Menu.handle_events/update/draw
  ├─ State.PLAYING → World.update + Player.update + Enemies.update + HUD.draw
  ├─ State.PAUSED → Overlay + Menu pausa
  ├─ State.GAME_OVER → Pantalla + input reiniciar
  └─ State.VICTORY → Pantalla final + credits
```

### 3.3 Tilemap y Colisiones
- **Formato:** CSV simple (fácil de editar en Excel/Google Sheets) o Tiled (.tmx) con `pytmx`
- **Capas:** `ground` (decorativo), `walls` (colisión), `spawns` (jugador, enemigos, pickups), `doors` (transiciones)
- **Tamaño tile:** 16×16 o 32×32 px (recomendado 16×16 estilo GB/Zelda 1)

---

## 4. Distribución de Tareas (6 Integrantes)

### Roles y Responsabilidades

| Integrante | Rol Principal | Entregables Clave | Dependencias |
|------------|---------------|-------------------|--------------|
| **Líder Técnico / Core** | Arquitectura, game loop, state machine, camera, build/release | `core/game.py`, `core/camera.py`, `core/events.py`, `main.py`, `config.py` | Base para todos |
| **Jugador & Combate** | Player, movimiento, input, ataque, invulnerabilidad, stats | `entities/player.py`, `entities/projectile.py`, `systems/combat.py` | Core, Entidades base |
| **Enemigos & IA** | Enemigos base, 3 tipos, pathfinding simple, jefe final | `entities/enemy.py`, `entities/enemies/*.py`, `entities/boss.py`, `systems/pathfinding.py` | Core, Entidades base, Combate |
| **Mundo & Niveles** | Tilemap, habitaciones, dungeon, transiciones, puertas/llaves | `world/tilemap.py`, `world/room.py`, `world/dungeon.py`, `world/level_data/` | Core, Camera |
| **UI & UX** | HUD, menús, game over, victory, pause, sonidos básicos | `ui/hud.py`, `ui/menus.py`, `ui/dialogue.py`, integración sonidos | Core, Player stats |
| **Assets & QA** | Sprites, animaciones, sonidos, testing, bug tracking, doc | `assets/` (organizados), `utils/animation.py`, testing manual, README | Todos (entrega continua) |

### Matriz de Dependencias (orden de implementación)

```
SEMANA 1                          SEMANA 2                        SEMANA 3                        SEMANA 4
├─ Core: game loop, states        ├─ Player: movimiento + ataque  ├─ Dungeon: habitaciones +      ├─ Integración completa
├─ Config + constants             ├─ Combate: daño, knockback     │   transiciones                ├─ Jefe final pulido
├─ Entity base + sprites          ├─ Enemigos: 3 tipos + IA       ├─ Llaves/puertas + progresión  ├─ Game Over / Victory
├─ Tilemap básico + colisiones    ├─ Pickups: corazón, moneda     ├─ HUD completo + menús         ├─ Balanceo dificultad
├─ Camera follow                  ├─ Pathfinding básico           ├─ Save/load (checkpoint)       ├─ Testing + fixes
│                                 │                                 │                                 ├─ Documentación final
│                                 │                                 │                                 └─ Build release
```

### Reglas de Trabajo en Equipo (Anti-conflictos)

1. **Rama por feature:** `feature/player-movement`, `feature/enemy-ai`, `feature/dungeon-system`, etc.
2. **PR obligatorios:** Ningún push directo a `main`. Mínimo 1 revisión.
3. **Interfaces compartidas en `core/` y `entities/entity.py`** — no tocar sin avisar.
4. **Assets centralizados:** `assets/` solo los modifica el integrante de Assets; otros piden cambios por issue.
5. **Daily sync 15 min:** Qué hice, qué haré, bloqueos.
6. **Definición de "Done":** Funciona + sin warnings lint + probado en 2 resoluciones.

---

## 5. Hitos y Entregas (4 Semanas)

| Hito | Fecha Target | Criterios de Aceptación |
|------|--------------|-------------------------|
| **H0: Setup** | Día 1-2 | Repo clonado, pygame corre, ventana 640×480/960×720, FPS 60, git flow definido |
| **H1: Core Jugable** | Fin Semana 1 | Player se mueve, colisiona con paredes, cámara sigue, cambia estado MENU→PLAYING→PAUSE |
| **H2: Combate Básico** | Fin Semana 2 | Player ataca → enemigo recibe daño → muere → drop moneda/corazón; 3 tipos enemigos funcionales |
| **H3: Mundo Conectado** | Fin Semana 3 | 4-6 habitaciones conectadas, llaves abren puertas, boss room accesible, HUD completo |
| **H4: Juego Completo** | Fin Semana 4 | Jefe final con 2 fases, Game Over/Victoria, save/load, menús pulidos, build .exe/.app |

---

## 6. Riesgos y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Scope creep (añadir features) | Alta | Alto | **Freeze de features en H2**; todo lo nuevo = backlog post-entrega |
| Merge conflicts en `core/` | Media | Alto | Ramas cortas (<3 días), PRs pequeños, owner de `core/` = Líder Técnico |
| Assets no llegan a tiempo | Media | Medio | Placeholders programados (rectángulos de colores) desde H0; assets reales en paralelo |
| Un integrante se retrasa | Alta | Alto | Pair programming semanal; tareas "stretch" asignadas a quien termine antes |
| Pathfinding muy complejo | Media | Medio | Empezar con IA simple (move toward player + evitar paredes); A* solo si tiempo |
| Dificultad injusta | Media | Medio | Playtesting interno desde H2; valores en `config.py` para tweak rápido |

---

## 7. Decisiones Técnicas Pendientes (Necesitan Confirmación)

1. **Tilemap:** ¿CSV casero (más control, menos features) o **Tiled + pytmx** (editor visual, capas, objetos)?  
   → *Recomendación: Tiled si alguien aprende rápido; si no, CSV.*

2. **Resolución / Escalado:** ¿Ventana fija 640×480 (pixel perfect ×3 = 1920×1440) o escalable con `pygame.transform.scale`?  
   → *Recomendación: Fija 640×480 surface interna → escalar a pantalla completa.*

3. **Sprites:** ¿Dibujan ustedes (programmer art), usan assets libres (itch.io/opengameart), o mix?  
   → *Definir paleta y estilo día 1 para consistencia.*

4. **Sonidos:** ¿Generan con sfxr/bfxr o buscan libres?  
   → *sfxr es rápido y encaja estética retro.*

5. **Build final:** ¿`pyinstaller` (Windows) + `py2app` (Mac) o solo distribución código + requirements?  
   → *PyInstaller one-file para Windows es estándar.*

---

## 8. Próximos Pasos Inmediatos (Esta Semana)

1. **Crear repo** + `.gitignore` + `requirements.txt` (pygame, pytmx si usan Tiled)
2. **Definir convención de código:** type hints, naming (snake_case), docstrings mínimas
3. **Configurar linting:** `ruff` o `flake8` + `black` (formateo automático en pre-commit)
4. **Bocetar primer mapa** en papel/Tiled: 3-4 habitaciones, spawn player, 2 enemigos, 1 cofre, 1 puerta con llave
5. **Asignar dueños** a cada módulo de la tabla de la Sección 4