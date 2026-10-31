import csv
import os
from datetime import date

ARCHIVO_EQUIPOS = "equipos.csv"
ARCHIVO_USUARIOS = "usuarios.csv"
ARCHIVO_PRESTAMOS = "prestamos.csv"

CAMPOS_EQUIPOS = ["codigo", "nombre", "marca", "categoria", "cantidad_total"]
CAMPOS_USUARIOS = ["identificador", "nombre", "tipo", "seccion"]
CAMPOS_PRESTAMOS = ["id_prestamo", "codigo_equipo", "identificador_usuario",
                    "fecha_prestamo", "fecha_devolucion_prevista",
                    "fecha_devolucion_real", "estado"]

def leer_csv(ruta, campos):
    if not os.path.exists(ruta):
        with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
        return []
    with open(ruta, "r", newline="", encoding="utf-8-sig") as archivo:
        return list(csv.DictReader(archivo))

def guardar_csv(ruta, campos, filas):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(filas)

def cargar_datos():
    return (leer_csv(ARCHIVO_EQUIPOS, CAMPOS_EQUIPOS),
            leer_csv(ARCHIVO_USUARIOS, CAMPOS_USUARIOS),
            leer_csv(ARCHIVO_PRESTAMOS, CAMPOS_PRESTAMOS))

def guardar_todo(equipos, usuarios, prestamos):
    guardar_csv(ARCHIVO_EQUIPOS, CAMPOS_EQUIPOS, equipos)
    guardar_csv(ARCHIVO_USUARIOS, CAMPOS_USUARIOS, usuarios)
    guardar_csv(ARCHIVO_PRESTAMOS, CAMPOS_PRESTAMOS, prestamos)

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("El dato no puede quedar vacío.")

def buscar_equipo(equipos, codigo):
    return next((e for e in equipos if e["codigo"].lower() == codigo.lower()), None)

def buscar_usuario(usuarios, identificador):
    return next((u for u in usuarios if u["identificador"].lower() == identificador.lower()), None)

def prestamos_activos(prestamos, codigo=None):
    return [p for p in prestamos if p["estado"] == "ACTIVO"
            and (codigo is None or p["codigo_equipo"].lower() == codigo.lower())]

def disponibles(equipos, prestamos, equipo):
    prestados = len(prestamos_activos(prestamos, equipo["codigo"]))
    return int(equipo["cantidad_total"]) - prestados

def registrar_equipo(equipos):
    print("\n--- REGISTRO DE EQUIPO ---")
    codigo = pedir_texto("Código único (ej. EQ001): ")
    if buscar_equipo(equipos, codigo):
        print("Error: ese código ya existe.")
        return
    nombre = pedir_texto("Nombre del equipo: ")
    marca = pedir_texto("Marca/fabricante: ")
    categoria = pedir_texto("Categoría: ")
    while True:
        try:
            cantidad = int(pedir_texto("Cantidad total (entero mayor que 0): "))
            if cantidad > 0:
                break
            print("La cantidad debe ser mayor que cero.")
        except ValueError:
            print("Escriba un número entero.")
    equipos.append({"codigo": codigo, "nombre": nombre, "marca": marca,
                    "categoria": categoria, "cantidad_total": str(cantidad)})
    print("Equipo registrado correctamente.")

def registrar_usuario(usuarios):
    print("\n--- REGISTRO DE USUARIO ---")
    identificador = pedir_texto("Identificador único (ej. U001): ")
    if buscar_usuario(usuarios, identificador):
        print("Error: ese identificador ya existe.")
        return
    nombre = pedir_texto("Nombre completo: ")
    while True:
        tipo = pedir_texto("Tipo (Estudiante/Docente): ").capitalize()
        if tipo in ("Estudiante", "Docente"):
            break
        print("Escriba Estudiante o Docente.")
    seccion = pedir_texto("Sección o área: ")
    usuarios.append({"identificador": identificador, "nombre": nombre,
                     "tipo": tipo, "seccion": seccion})
    print("Usuario registrado correctamente.")

def registrar_prestamo(equipos, usuarios, prestamos):
    print("\n--- NUEVO PRÉSTAMO ---")
    codigo = pedir_texto("Código del equipo: ")
    equipo = buscar_equipo(equipos, codigo)
    if not equipo:
        print("No existe ese equipo.")
        return
    if disponibles(equipos, prestamos, equipo) <= 0:
        print("No hay unidades disponibles de ese equipo.")
        return
    identificador = pedir_texto("Identificador del usuario: ")
    usuario = buscar_usuario(usuarios, identificador)
    if not usuario:
        print("No existe ese usuario. Regístrelo primero.")
        return
    fecha_prestamo = date.today().isoformat()
    fecha_prevista = pedir_texto("Fecha prevista de devolución (AAAA-MM-DD): ")
    try:
        date.fromisoformat(fecha_prevista)
    except ValueError:
        print("Formato de fecha incorrecto. Use AAAA-MM-DD.")
        return
    nuevo_id = "P" + str(max([int(p["id_prestamo"][1:]) for p in prestamos
                              if p["id_prestamo"].startswith("P") and p["id_prestamo"][1:].isdigit()]
                             + [0]) + 1).zfill(3)
    prestamos.append({"id_prestamo": nuevo_id, "codigo_equipo": equipo["codigo"],
                      "identificador_usuario": usuario["identificador"],
                      "fecha_prestamo": fecha_prestamo,
                      "fecha_devolucion_prevista": fecha_prevista,
                      "fecha_devolucion_real": "", "estado": "ACTIVO"})
    print(f"Préstamo registrado. Número: {nuevo_id}. Fecha: {fecha_prestamo}")

def registrar_devolucion(equipos, usuarios, prestamos):
    print("\n--- DEVOLUCIÓN DE EQUIPO ---")
    id_prestamo = pedir_texto("Número de préstamo (ej. P001): ").upper()
    prestamo = next((p for p in prestamos if p["id_prestamo"].upper() == id_prestamo), None)
    if not prestamo:
        print("No existe ese préstamo.")
        return
    if prestamo["estado"] == "DEVUELTO":
        print("Este préstamo ya fue devuelto. No se permite duplicar la devolución.")
        return
    prestamo["estado"] = "DEVUELTO"
    prestamo["fecha_devolucion_real"] = date.today().isoformat()
    print("Devolución registrada correctamente.")

def buscar_y_mostrar(equipos, prestamos):
    termino = pedir_texto("Escriba código o nombre del equipo: ").lower()
    encontrados = [e for e in equipos if termino in e["codigo"].lower()
                   or termino in e["nombre"].lower()]
    if not encontrados:
        print("No se encontraron equipos.")
        return
    for e in encontrados:
        print(f'{e["codigo"]} | {e["nombre"]} | {e["marca"]} | '
              f'Disponibles: {disponibles(equipos, prestamos, e)} de {e["cantidad_total"]}')

def listar_prestamos(equipos, usuarios, prestamos, solo_activos=False):
    filas = [p for p in prestamos if not solo_activos or p["estado"] == "ACTIVO"]
    if not filas:
        print("No hay préstamos para mostrar.")
        return
    print("\nID | EQUIPO | USUARIO | FECHA | DEVOLUCIÓN PREVISTA | ESTADO")
    for p in filas:
        equipo = buscar_equipo(equipos, p["codigo_equipo"])
        usuario = buscar_usuario(usuarios, p["identificador_usuario"])
        nombre_equipo = equipo["nombre"] if equipo else p["codigo_equipo"]
        nombre_usuario = usuario["nombre"] if usuario else p["identificador_usuario"]
        print(f'{p["id_prestamo"]} | {nombre_equipo} | {nombre_usuario} | '
              f'{p["fecha_prestamo"]} | {p["fecha_devolucion_prevista"]} | {p["estado"]}')

def mostrar_resumen(equipos, usuarios, prestamos):
    total_unidades = sum(int(e["cantidad_total"]) for e in equipos)
    total_prestados = len(prestamos_activos(prestamos))
    print("\n--- RESUMEN DEL SISTEMA ---")
    print(f"Tipos de equipo registrados: {len(equipos)}")
    print(f"Unidades totales registradas: {total_unidades}")
    print(f"Usuarios registrados: {len(usuarios)}")
    print(f"Préstamos históricos: {len(prestamos)}")
    print(f"Préstamos activos: {total_prestados}")
    print(f"Unidades actualmente prestadas: {total_prestados}")
    print(f"Unidades disponibles: {total_unidades - total_prestados}")

def mostrar_menu():
    print("""
=========================================
 SISTEMA DE PRÉSTAMOS DE EQUIPO ESCOLAR
=========================================
1. Registrar equipo
2. Registrar usuario
3. Registrar préstamo
4. Registrar devolución
5. Buscar equipo y disponibilidad
6. Mostrar préstamos activos
7. Mostrar historial de préstamos
8. Mostrar resumen
9. Guardar y salir
""")

def main():
    equipos, usuarios, prestamos = cargar_datos()

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-9): ").strip()

        if opcion == "1":
            registrar_equipo(equipos)
        elif opcion == "2":
            registrar_usuario(usuarios)
        elif opcion == "3":
            registrar_prestamo(equipos, usuarios, prestamos)
        elif opcion == "4":
            registrar_devolucion(equipos, usuarios, prestamos)
        elif opcion == "5":
            buscar_y_mostrar(equipos, prestamos)
        elif opcion == "6":
            listar_prestamos(equipos, usuarios, prestamos, True)
        elif opcion == "7":
            listar_prestamos(equipos, usuarios, prestamos, False)
        elif opcion == "8":
            mostrar_resumen(equipos, usuarios, prestamos)
        elif opcion == "9":
            guardar_todo(equipos, usuarios, prestamos)
            print("Datos guardados. Hasta pronto.")
            break
        else:
            print("Opción incorrecta. Seleccione del 1 al 9.")


if __name__ == "__main__":
    main()