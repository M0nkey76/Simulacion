from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import unlit_shader
import random
import math

window.icon = 'itverico.ico'
app = Ursina()

# CONFIG DE LA VENTANA
window.title = 'Laberinto 3D - Escape'
window.borderless = False
window.fullscreen = False

# Lista para guardar todas las sombras
todas_las_sombras = []

def crear_sombra_dinamica(entidad, escala_extra=1.3, alpha=70, offset_y=0.05):

    
    try:
        
        scale = entidad.scale
       
        if not isinstance(scale, (tuple, list)):
           
            if isinstance(scale, (int, float)):
                scale = (scale, scale, scale)
            else:
               
                try:
                    scale = (scale.x, scale.y, scale.z)
                except:
                    scale = (1, 1, 1)
        
        if len(scale) >= 3:
            sx = scale[0] * escala_extra
            sz = scale[2] * escala_extra
        elif len(scale) == 2:
            sx = scale[0] * escala_extra
            sz = scale[1] * escala_extra
        else:
            sx = scale[0] * escala_extra
            sz = scale[0] * escala_extra
            
    except (AttributeError, IndexError, TypeError) as e:
        print(f"⚠️ Advertencia: No se pudo obtener scale de {entidad}. Error: {e}")
        sx = 2 * escala_extra
        sz = 2 * escala_extra
    
    sombra = Entity(
        model='quad',
        scale=(sx, sz),
        position=(entidad.x, offset_y + 0.01, entidad.z),
        rotation_x=90,
        color=color.rgba(0, 0, 0, alpha),
        eternal=True,
        shader=unlit_shader,
        always_on_top=True,
        render_queue=1
    )
    
    
    sombra.objeto_padre = entidad
    sombra.escala_original = (sx, sz)
    sombra.alpha_original = alpha
    sombra.offset_y = offset_y
    
    
    entidad.sombra = sombra
    
  
    todas_las_sombras.append(sombra)
    
    return sombra

def actualizar_todas_las_sombras():
    for sombra in todas_las_sombras[:]:
      
        if not hasattr(sombra, 'objeto_padre') or sombra.objeto_padre is None:
            todas_las_sombras.remove(sombra)
            destroy(sombra)
            continue
            
        objeto = sombra.objeto_padre
        
        
        sombra.position = (objeto.x, sombra.offset_y + 0.01, objeto.z)
        
        
        if hasattr(objeto, 'y'):
            altura = max(0, objeto.y)
            nuevo_alpha = max(20, sombra.alpha_original - altura * 15)
            sombra.color = color.rgba(0, 0, 0, int(nuevo_alpha))
        
        
        if hasattr(objeto, 'y') and objeto.y > 0:
            factor_crecimiento = 1.0 + (objeto.y * 0.1)
            nueva_escala_x = sombra.escala_original[0] * factor_crecimiento
            nueva_escala_z = sombra.escala_original[1] * factor_crecimiento
            sombra.scale = (nueva_escala_x, nueva_escala_z)
        
        
        if hasattr(objeto, 'rotation_y'):
            sombra.rotation_y = objeto.rotation_y

def eliminar_sombra(entidad):
    """Elimina la sombra asociada a una entidad"""
    if hasattr(entidad, 'sombra'):
        if entidad.sombra in todas_las_sombras:
            todas_las_sombras.remove(entidad.sombra)
        destroy(entidad.sombra)
        entidad.sombra = None


piso = Entity(
    model='cube',
    scale=(100, 0.5, 100),
    texture='plataforma',
    texture_scale=(2, 2),
    collider='box',
    color=color.white
)

L = 50
ALTURA = 8

paredes = []
config_pared = {
    'model': 'cube',
    'texture': 'bosqueNubes',
    'texture_scale': (8, 1),
    'color': color.azure,
    'collider': 'box'
}


paredes.append(Entity(scale=(L, ALTURA, 1), position=(0, ALTURA/2, L/2), **config_pared))
paredes.append(Entity(scale=(L, ALTURA, 1), position=(0, ALTURA/2, -L/2), **config_pared))
paredes.append(Entity(scale=(1, ALTURA, L), position=(L/2, ALTURA/2, 0), **config_pared))
paredes.append(Entity(scale=(1, ALTURA, L), position=(-L/2, ALTURA/2, 0), **config_pared))


print(f"✅ Paredes exteriores creadas: {len(paredes)}")

print("Generando laberinto...")

lab_size = 10
cell_size = 4
maze_walls = []

for x in range(lab_size):
    for z in range(lab_size):
        world_x = (x - lab_size/2) * cell_size
        world_z = (z - lab_size/2) * cell_size
        
        if random.random() > 0.6:
            if random.choice([True, False]):
                wall = Entity(
                    model='cube',
                    texture='plataforma',
                    texture_scale=(2, 2),
                    color=color.white,
                    scale=(0.5, ALTURA, cell_size),
                    position=(world_x, ALTURA/2, world_z),
                    collider='box'
                )
                maze_walls.append(wall)
                
            else:
                wall = Entity(
                    model='cube',
                    color=color.white,
                    scale=(cell_size, ALTURA, 0.5),
                    texture='plataforma',
                    texture_scale=(2, 2),
                    position=(world_x, ALTURA/2, world_z),
                    collider='box'
                )
                maze_walls.append(wall)
                

entrance_x = -L/2 + 5
entrance_z = 0
exit_x = L/2 - 5
exit_z = 0

paredes_a_eliminar_entrada = []
paredes_a_eliminar_salida = []


for wall in maze_walls:
    if abs(wall.x - entrance_x) < 3 and abs(wall.z - entrance_z) < 3:
        paredes_a_eliminar_entrada.append(wall)
    if abs(wall.x - exit_x) < 3 and abs(wall.z - exit_z) < 3:
        paredes_a_eliminar_salida.append(wall)


for wall in paredes_a_eliminar_entrada:
    if wall in maze_walls:
        eliminar_sombra(wall)
        destroy(wall)
        maze_walls.remove(wall)

for wall in paredes_a_eliminar_salida:
    if wall in maze_walls:
        eliminar_sombra(wall)
        destroy(wall)
        maze_walls.remove(wall)


exit_area = Entity(
    model='cube',
    texture='plataforma',
    scale=(cell_size*2, 0.5, cell_size*2),
    position=(exit_x, 0.25, exit_z),
    color=color.rgba(0, 255, 0, 100),
    collider='box'
)


print(f"✅ Laberinto generado con {len(maze_walls)} paredes")

for i in range(8):
    lamp_x = random.uniform(-L/2 + 5, L/2 - 5)
    lamp_z = random.uniform(-L/2 + 5, L/2 - 5)
    
    lamp_post = Entity(
        model='cube',
        scale=(0.5, 4, 0.5),
        position=(lamp_x, 2, lamp_z),
        color=color.dark_gray
    )

    crear_sombra_dinamica(lamp_post, escala_extra=1.2, alpha=100, offset_y=0.1)
    
    lamp_light = Entity(
        model='cube',
        scale=(1, 1, 1),
        position=(lamp_x, 4.5, lamp_z),
        color=color.yellow,
        shader=unlit_shader
    )
    
    PointLight(
        position=(lamp_x, 4, lamp_z),
        color=color.yellow,
        attenuation=(1, 0.1, 0.01)
    )


objetos_recolectables = []
for i in range(15):
    obj_x = random.uniform(-L/2 + 3, L/2 - 3)
    obj_z = random.uniform(-L/2 + 3, L/2 - 3)
    
    if i % 3 == 0:
        obj = Entity(
            model='cube',
            texture='colormap',
            position=(obj_x, 1, obj_z),
            scale=(0.8, 0.8, 0.8),
            color=color.red
        )
    elif i % 3 == 1:
        obj = Entity(
            model='sphere',
            texture='colormapA',
            position=(obj_x, 1, obj_z),
            scale=(0.8, 0.8, 0.8),
            color=color.blue
        )
    else:
        obj = Entity(
            model='cube',
            texture='colormapA',
            position=(obj_x, 1, obj_z),
            scale=(0.8, 1.2, 0.8),
            color=color.gold
        )
    
    obj.collider = 'sphere'
    objetos_recolectables.append(obj)
    
    crear_sombra_dinamica(obj, escala_extra=1.3, alpha=120, offset_y=0.1)

enemigos = []
for i in range(3):
    enemy = Entity(
        model='cube',
        scale=(1, 1, 1),
        position=(random.uniform(-L/2 + 5, L/2 - 5), 0.5, random.uniform(-L/2 + 5, L/2 - 5)),
        color=color.pink,
        collider='box'
    )
    enemigos.append(enemy)
    

AmbientLight(color=color.rgba(80, 80, 100, 0.3))
moon = DirectionalLight()
moon.look_at(Vec3(-1, -1, 0.2))
moon.color = color.rgb(150, 150, 200)


player = FirstPersonController()
player.position = (entrance_x, 9, entrance_z)
player.gravity = 0.5
player.cursor.visible = False
player.speed = 6
player.jump_height = 0


player_sombra = crear_sombra_dinamica(player, escala_extra=0.8, alpha=80, offset_y=0.1)

score = 0
objetos_recolectados = 0
en_meta = False
juego_terminado = False  
tiempo_final = None  

score_text = Text(
    text=f"Objetos: {objetos_recolectados}/15",
    position=(-0.85, 0.45),
    scale=1.5,
    color=color.white
)

meta_text = Text(
    text="",
    position=(0, 0.4),
    scale=2,
    color=color.green
)

from datetime import datetime
start_time = datetime.now()
time_text = Text(
    text="Tiempo: 00:00",
    position=(-0.85, 0.4),
    scale=1.5,
    color=color.cyan
)

tiempo_final_text = Text(
    text="",
    position=(0, 0.2),
    scale=2,
    color=color.gold,
    enabled=False  
)

inst_text = Text(
    text="Encuentra los 15 objetos y llega a la salida verde",
    position=(0, -0.45),
    scale=1.2,
    color=color.yellow
)

shadow_info = Text(
    text="Sombras: VISIBLES (Presiona K para ocultar)",
    position=(0.7, 0.45),
    scale=1.2,
    color=color.light_gray
)


pause_panel = Entity(model='quad', scale=(0.5, 0.4), enabled=False, color=color.rgba(0, 0, 0, 200))
Text("LABERINTO PAUSADO", parent=pause_panel, y=.15, scale=2, color=color.white)

game_paused = False

def toggle_pause():
    global game_paused
    if juego_terminado:
        return  
    game_paused = not game_paused
    pause_panel.enabled = game_paused
    player.enabled = not game_paused
    mouse.locked = not game_paused
    mouse.visible = game_paused

Button(text="Reanudar", parent=pause_panel, y=0.02, scale=(0.4, 0.1), 
       color=color.green, on_click=toggle_pause)
Button(text="Salir", parent=pause_panel, y=-0.15, scale=(0.4, 0.1), 
       color=color.red, on_click=application.quit)

def update():
    global score, objetos_recolectados, en_meta, juego_terminado, tiempo_final
    
    if game_paused:
        return
    

    if not juego_terminado:

        current_time = datetime.now()
        elapsed = current_time - start_time
        minutes = elapsed.seconds // 60
        seconds = elapsed.seconds % 60
        time_text.text = f"Tiempo: {minutes:02d}:{seconds:02d}"
    

    for obj in objetos_recolectables[:]:
        if distance(player.position, obj.position) < 2:
     
            eliminar_sombra(obj)
            

            destroy(obj)
            objetos_recolectables.remove(obj)
            

            objetos_recolectados += 1
            score += 100
            score_text.text = f"Objetos: {objetos_recolectados}/15  Puntos: {score}"
 
    for enemy in enemigos[:]:
        if distance(player.position, enemy.position) < 1.5:
            player.position = (entrance_x, 2, entrance_z)
    
 
    if distance(player.position, exit_area.position) < 3 and not en_meta:
        if objetos_recolectados == 15:
            en_meta = True
            juego_terminado = True  
            tiempo_final = datetime.now()  
            
            
            elapsed = tiempo_final - start_time
            minutes = elapsed.seconds // 60
            seconds = elapsed.seconds % 60
            
            
            meta_text.text = "¡LABERINTO COMPLETADO!"
            
           
            tiempo_final_text.text = f"Tiempo final: {minutes:02d}:{seconds:02d}"
            tiempo_final_text.enabled = True
            
            
            player.enabled = False
            mouse.locked = False
            mouse.visible = True
            
            
            print(f"🎉 ¡Juego terminado! Tiempo: {minutes:02d}:{seconds:02d}")
            
        else:
            meta_text.text = f"Necesitas {15 - objetos_recolectados} objetos más"
            invoke(setattr, meta_text, 'text', '', delay=2)
    
    
    if not juego_terminado:
        
        for enemy in enemigos:
            enemy.x += math.sin(time.time() + id(enemy)/1000) * 0.02
            enemy.z += math.cos(time.time() + id(enemy)/1000) * 0.02
        
        
        for obj in objetos_recolectables:
            obj.rotation_y += 1
        
        
        if held_keys['shift']:
            player.speed = 10
        else:
            player.speed = 6
        
        
        if player.y < -10:
            player.position = (entrance_x, 2, entrance_z)
    
    
    actualizar_todas_las_sombras()



sombra_visible = True

def input(key):
    global sombra_visible
    
    if key == 'escape':
        toggle_pause()
    
    if key == 'r' and held_keys['control']:
        print("Reiniciando juego...")
        application.quit()
    
    
    if key == 'k':
        sombra_visible = not sombra_visible
        for sombra in todas_las_sombras:
            sombra.enabled = sombra_visible
        shadow_info.text = f"Sombras: {'VISIBLES' if sombra_visible else 'OCULTAS'} (Presiona K)"



print("=" * 50)
print("LABERINTO 3D INICIADO")
print("=" * 50)
print("✨ SISTEMA DE SOMBRAS ACTIVADO:")
print(f"   • {len(todas_las_sombras)} sombras creadas")
print("   • Presiona 'K' para mostrar/ocultar sombras")
print("   • Piso gris para mejor contraste")
print("")
print("CONTROLES:")
print("WASD - Movimiento")
print("SHIFT - Correr")
print("K - Mostrar/ocultar sombras")
print("ESC - Pausa")
print("Ctrl+R - Reiniciar")
print("=" * 50)

app.run()