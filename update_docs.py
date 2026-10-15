# Script to update documentation files to remove boss and music references

import re

def update_tareas():
    with open('docs/TAREAS_POR_INTEGRANTE.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Leslie section
    old_leslie = """### 🎨 Integrante 6 - Leslie (Assets & QA Lead)

**Semana 1 (continuo):**
- [ ] Estructura `assets/`:
  ```
  assets/
  ├── sprites/
  │   ├── player/        # idle.png, walk_1-4.png, shoot.png, hurt.png (3 armas)
  │   ├── enemies/       # basic/, tank/, speedy/, boss/
  │   ├── weapons/       # pistol.png, shotgun.png, rifle.png, projectiles/
  │   ├── barrier/       # barrier_1-4.png, barrier_destroyed.png
  │   ├── ui/            # heart_full.png, heart_empty.png, coin.png
  │   └── particles/     # spark.png, smoke.png
  ├── sounds/
  │   ├── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)
  │   └── music/         # main_loop.ogg, boss_loop.ogg
  └── fonts/             # .ttf pixel art (ej. PressStart2P, Pixeloid)
  ```
- [ ] Placeholders día 1: rectángulos colores para TODOS sprites (permite trabajar al resto)

**Semana 2-3:**
- [ ] Sprites finales progresivos (prioridad: player → enemigos básicos → armas/proyectiles → barreras → boss → UI → partículas)
- [ ] `utils/animation.py` - Clase Animation: frames (list[Surface]), duration, loop, flip_h, flip_v, get_frame(dt)
- [ ] Sonidos generados con sfxr/bfxr + música libre (opengameart/itch.io)"""

    new_leslie = """### 🎨 Integrante 6 - Leslie (Assets & QA Lead)

**Semana 1 (continuo):**
- [ ] Estructura `assets/`:
  ```
  assets/
  ├── sprites/
  │   ├── player/        # idle.png, walk_1-4.png, shoot.png, hurt.png (3 armas)
  │   ├── enemies/       # basic/, tank/, speedy/
  │   ├── weapons/       # pistol.png, shotgun.png, rifle.png, projectiles/
  │   ├── barrier/       # barrier_1-4.png, barrier_destroyed.png
  │   ├── ui/            # heart_full.png, heart_empty.png, coin.png
  │   └── particles/     # spark.png, smoke.png
  ├── sounds/
  │   └── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)
  └── fonts/             # .ttf pixel art (ej. PressStart2P, Pixeloid)
  ```
- [ ] Placeholders día 1: rectángulos colores para TODOS sprites (permite trabajar al resto)

**Semana 2-3:**
- [ ] Sprites finales progresivos (prioridad: player → enemigos básicos → armas/proyectiles → barreras → UI → partículas)
- [ ] `utils/animation.py` - Clase Animation: frames (list[Surface]), duration, loop, flip_h, flip_v, get_frame(dt)
- [ ] Sonidos generados con sfxr/bfxr + música libre (opengameart/itch.io)"""

    content = content.replace(old_leslie, new_leslie)
    
    with open('docs/TAREAS_POR_INTEGRANTE.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("TAREAS_POR_INTEGRANTE.md updated")

def update_analisis():
    with open('docs/ANALISIS_Y_DISENO.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove boss from enemies table
    content = content.replace(
        "| **Jefes (Boss)** | Oleada 5: máquina de estados, 3 fases, weak point, telegraphing | P0 |",
        ""
    )
    
    # Remove boss from enemies list
    content = content.replace(
        "| **Enemigos Básicos** | 3 tipos: Basic (estándar), Tank (HP alto, lento), Speedy (rápido, frágil) | P0 |\n| **Jefes (Boss)** | Oleada 5: máquina de estados, 3 fases, weak point, telegraphing | P0 |",
        "| **Enemigos Básicos** | 3 tipos: Basic (estándar), Tank (HP alto, lento), Speedy (rápido, frágil) | P0 |"
    )
    
    # Remove boss from entities/enemies
    content = content.replace(
        "│   ├── enemies/       # basic/, tank/, speedy/, boss/",
        "│   ├── enemies/       # basic/, tank/, speedy/"
    )
    
    # Remove music folder
    content = content.replace(
        "├── sounds/\n│   ├── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)\n│   └── music/         # main_loop.ogg, boss_loop.ogg",
        "├── sounds/\n│   └── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)"
    )
    
    # Remove boss from Lilian's tasks
    content = content.replace(
        "- [ ] `entities/enemies/boss.py` - Boss oleada 5: 3 fases, hp 500→300→200, patrones: radial burst, charge, summon basics. Weak point: brilla 3s cada fase.",
        ""
    )
    
    # Remove boss from Zebedeo's tasks
    content = content.replace(
        "- [ ] Screen shake en: player hit, boss hit, wave complete",
        "- [ ] Screen shake en: player hit, wave complete"
    )
    
    # Remove music from Aron's tasks
    content = content.replace(
        "- [ ] Integración sonidos: `assets/sounds/` (sfx: shoot, hit, kill, coin, upgrade, wave_start, game_over + música loop 2 tracks)",
        "- [ ] Integración sonidos: `assets/sounds/` (sfx: shoot, hit, kill, coin, upgrade, wave_start, game_over)"
    )
    
    # Remove music from Leslie's assets
    content = content.replace(
        "├── sounds/\n│   ├── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)\n│   └── music/         # main_loop.ogg, boss_loop.ogg",
        "├── sounds/\n│   └── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)"
    )
    
    # Remove music folder from assets structure
    content = content.replace(
        "├── sounds/\n│   ├── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)\n│   └── music/         # main_loop.ogg, boss_loop.ogg",
        "├── sounds/\n│   └── sfx/           # .wav/.ogg (shoot, hit, kill, coin, upgrade, wave, hurt)"
    )
    
    # Remove boss references from QA checklist
    content = content.replace(
        "- [ ] Wave 5: Boss aparece, 3 fases funcionan, weak point vulnerable",
        ""
    )
    content = content.replace(
        "- [ ] Enemigos: 3 tipos (Basic, Tank, Speedy) + 1 Boss, comportamientos distintos, mueren, dan oro",
        "- [ ] Enemigos: 3 tipos (Basic, Tank, Speedy), comportamientos distintos, mueren, dan oro"
    )
    content = content.replace(
        "- [ ] Animaciones fluidas (player, enemigos, boss)",
        "- [ ] Animaciones fluidas (player, enemigos)"
    )
    content = content.replace(
        "- [ ] Sonidos: disparo, impacto, muerte, moneda, upgrade, ola, música",
        "- [ ] Sonidos: disparo, impacto, muerte, moneda, upgrade, ola"
    )
    content = content.replace(
        "- [ ] 3 enemigos + 1 boss funcionales",
        "- [ ] 3 enemigos funcionales"
    )
    content = content.replace(
        "- [ ] 3 enemigos + 1 boss con comportamientos claros",
        "- [ ] 3 enemigos con comportamientos claros"
    )
    
    # Remove boss branch references
    content = content.replace(
        "  ├─ feature/boss-wave5\n  ├─ feature/boss-wave10\n",
        ""
    )
    
    with open('docs/ANALISIS_Y_DISENO.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("ANALISIS_Y_DISENO.md updated")


def update_hitos():
    with open('docs/HITOS_Y_ENTREGAS.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove boss from hito 2
    content = content.replace(
        "| **H2: Barreras fijas + Partículas + Upgrade Shop (6 fijos) + Boss** | Fin Semana 3 (26 oct) | Barreras fijas (4) con HP visible. Particle pool + screen shake. Upgrade Shop entre oleadas: 6 opciones fijas, compra con oro. Boss oleada 5 funcional (3 fases). |",
        "| **H2: Barreras fijas + Partículas + Upgrade Shop (6 fijos)** | Fin Semana 3 (26 oct) | Barreras fijas (4) con HP visible. Particle pool + screen shake. Upgrade Shop entre oleadas: 6 opciones fijas, compra con oro. |"
    )
    
    content = content.replace(
        "| **H2: Barreras fijas + Partículas + Upgrade Shop (6 fijos) + Boss** | Fin Semana 3 (26 oct) | Barreras fijas (4) con HP visible. Particle pool + screen shake. Upgrade Shop entre oleadas: 6 opciones fijas, compra con oro. Boss oleada 5 funcional (3 fases). |",
        "| **H2: Barreras fijas + Partículas + Upgrade Shop (6 fijos)** | Fin Semana 3 (26 oct) | Barreras fijas (4) con HP visible. Particle pool + screen shake. Upgrade Shop entre oleadas: 6 opciones fijas, compra con oro. |"
    )
    
    # Remove boss from hito 3
    content = content.replace(
        "| **H3: Contenido Completo + Polish** | Fin Semana 4 (2 nov) | Oleadas 1-10 balanceadas en JSON. Highscores persistentes top 10 + input nombre. Menús completos (main, pause, game over/victory compartida). Assets finales integrados. |",
        "| **H3: Contenido Completo + Polish** | Fin Semana 4 (2 nov) | Oleadas 1-10 balanceadas en JSON. Highscores persistentes top 10 + input nombre. Menús completos (main, pause, game over/victory compartida). Assets finales integrados. |"
    )
    
    # Remove boss wave 5 references
    content = content.replace(
        "**Objetivo:** Sistemas de profundidad: barreras fijas, partículas básicas, upgrade shop simplificado, boss wave 5.",
        "**Objetivo:** Sistemas de profundidad: barreras fijas, partículas básicas, upgrade shop simplificado."
    )
    content = content.replace(
        "- Boss oleada 5 (3 fases) | Lilian | HP 500, patrones: radial burst, charge, summon basics. Weak point brilla 3s/fase |",
        ""
    )
    content = content.replace(
        "- Boss oleada 5 se vence (3 fases)",
        ""
    )
    content = content.replace(
        "- Sonidos + música integrados | Leslie + Aron | SFX: shoot, hit, kill, coin, upgrade, wave, hurt + música loop 2 tracks (main + boss) |",
        "- Sonidos integrados | Leslie + Aron | SFX: shoot, hit, kill, coin, upgrade, wave, hurt |"
    )
    content = content.replace(
        "- 3 enemigos + 1 boss funcionales",
        "- 3 enemigos funcionales"
    )
    content = content.replace(
        "- Boss oleada 5 se vence (3 fases)",
        ""
    )
    content = content.replace(
        "- 3 enemigos + 1 boss con comportamientos claros",
        "- [ ] 3 enemigos con comportamientos claros"
    )
    content = content.replace(
        "- Boss oleada 5: 3 fases, hp 500→300→200, patrones: radial burst, charge, summon basics. Weak point: brilla 3s cada fase.",
        ""
    )
    content = content.replace(
        "| **4 - Zebedeo** | **Barriers & Particles** | Barreras fijas (4 posiciones, HP, draw), Particle Pool básico, Screen Shake, Debug | `entities/barrier.py`, `systems/particles.py`, `utils/debug.py` |",
        "| **4 - Zebedeo** | **Barriers & Particles** | Barreras fijas (4 posiciones, HP, draw), Particle Pool básico, Screen Shake, Debug | `entities/barrier.py`, `systems/particles.py`, `utils/debug.py` |"
    )
    
    with open('docs/HITOS_Y_ENTREGAS.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("HITOS_Y_ENTREGAS.md updated")


def update_reglas():
    with open('docs/REGLAS_EQUIPO.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove boss branches
    content = content.replace(
        "  ├─ feature/boss-wave5\n  ├─ feature/boss-wave10\n",
        ""
    )
    
    # Remove boss from must have
    content = content.replace(
        "| **Must Have** | Player movimiento+3 armas, 3 enemigos, 1 boss (oleada 5), oleadas 1-10, barreras fijas (4), upgrade shop (6 fijos), 3 vidas, game over/victory, highscores, HUD, menús, partículas básicas, build .exe |",
        "| **Must Have** | Player movimiento+3 armas, 3 enemigos, oleadas 1-10, barreras fijas (4), upgrade shop (6 fijos), 3 vidas, game over/victory, highscores, HUD, menús, partículas básicas, build .exe |"
    )
    
    # Remove boss from Lilian's responsibility
    content = content.replace(
        "| **Enemies & Waves** | Lilian | `entities/enemies/`, `entities/boss.py`, `systems/wave_manager.py`, `config/waves.json`, IA, spawning, balanceo oleadas |",
        "| **Enemies & Waves** | Lilian | `entities/enemies/`, `systems/wave_manager.py`, `config/waves.json`, IA, spawning, balanceo oleadas |"
    )
    
    # Remove boss branch from matrix
    
    with open('docs/REGLAS_EQUIPO.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print("REGLAS_EQUIPO.md updated")


if __name__ == "__main__":
    # Read files first to verify they exist
    import os
    for f in ['docs/TAREAS_POR_INTEGRANTE.md', 'docs/ANALISIS_Y_DISENO.md', 'docs/HITOS_Y_ENTREGAS.md', 'docs/REGLAS_EQUIPO.md']:
        if not os.path.exists(f):
            print(f"File not found: {f}")
        else:
            print(f"File exists: {f}")
    
    # Run the updates
    update_tareas()
    update_analisis()
    update_hitos()
    update_reglas()
    print("All documentation updated!")