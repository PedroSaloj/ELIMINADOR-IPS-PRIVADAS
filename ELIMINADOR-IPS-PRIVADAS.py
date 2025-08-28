#!/usr/bin/env python3
"""
Programa para filtrar direcciones IP públicas desde diferentes fuentes de entrada
y exportar el resultado a un archivo CSV.
"""

import csv
import ipaddress
import os
from datetime import datetime
from typing import List, Set


def es_ip_privada(ip_str: str) -> bool:
    """
    Verifica si una dirección IP es privada o reservada.
    
    Args:
        ip_str: String con la dirección IP a verificar
        
    Returns:
        True si la IP es privada/reservada, False si es pública
    """
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        
        # Verificar si es privada, loopback, link-local, etc.
        return (
            ip.is_private or
            ip.is_reserved or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_multicast or
            (isinstance(ip, ipaddress.IPv6Address) and ip.is_site_local)
        )
    except ValueError:
        # Si no es una IP válida, la consideramos como "privada" para excluirla
        print(f"  ⚠ IP inválida: {ip_str}")
        return True


def leer_ips_manual() -> Set[str]:
    """
    Permite al usuario ingresar IPs manualmente.
    
    Returns:
        Set de direcciones IP ingresadas
    """
    ips = set()
    print("\n📝 Ingrese las direcciones IP (una por línea)")
    print("   Escriba 'fin' para terminar:\n")
    
    while True:
        ip = input("IP> ").strip()
        if ip.lower() == 'fin':
            break
        if ip:
            ips.add(ip)
    
    return ips


def leer_ips_lista() -> Set[str]:
    """
    Lee IPs desde una lista predefinida en el código.
    
    Returns:
        Set de direcciones IP de la lista
    """
    # Lista de ejemplo - puedes modificarla según necesites
    lista_ips = [
        "192.168.1.1",      # Privada
        "10.0.0.1",         # Privada
        "8.8.8.8",          # Pública (Google DNS)
        "1.1.1.1",          # Pública (Cloudflare DNS)
        "172.16.0.1",       # Privada
        "208.67.222.222",   # Pública (OpenDNS)
        "127.0.0.1",        # Loopback
        "169.254.1.1",      # Link-local
        "224.0.0.1",        # Multicast
        "93.184.216.34",    # Pública (example.com)
        "192.168.100.50",   # Privada
        "142.251.41.14",    # Pública (google.com)
    ]
    
    print("\n📋 Lista predefinida cargada con {} IPs".format(len(lista_ips)))
    return set(lista_ips)


def leer_ips_csv() -> Set[str]:
    """
    Lee IPs desde un archivo CSV.
    
    Returns:
        Set de direcciones IP leídas del CSV
    """
    ips = set()
    
    archivo = input("\n📁 Ingrese la ruta del archivo CSV: ").strip()
    
    if not os.path.exists(archivo):
        print(f"  ❌ Error: El archivo '{archivo}' no existe")
        return ips
    
    try:
        with open(archivo, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                for campo in row:
                    # Limpiar y agregar cada IP encontrada
                    ip = campo.strip()
                    if ip:
                        ips.add(ip)
        
        print(f"  ✅ Se leyeron {len(ips)} IPs del archivo")
    except Exception as e:
        print(f"  ❌ Error al leer el archivo: {e}")
    
    return ips


def filtrar_ips_publicas(ips: Set[str]) -> List[str]:
    """
    Filtra solo las IPs públicas de un conjunto de IPs.
    
    Args:
        ips: Set de direcciones IP a filtrar
        
    Returns:
        Lista de IPs públicas ordenadas
    """
    ips_publicas = []
    
    print("\n🔍 Analizando IPs...")
    for ip in ips:
        if not es_ip_privada(ip):
            ips_publicas.append(ip)
            print(f"  ✓ {ip} - Pública")
        else:
            print(f"  ✗ {ip} - Privada/Reservada")
    
    return sorted(ips_publicas)


def guardar_resultado_csv(ips_publicas: List[str]) -> str:
    """
    Guarda las IPs públicas en un archivo CSV dentro de la carpeta 'output'.
    
    Args:
        ips_publicas: Lista de IPs públicas a guardar
        
    Returns:
        Ruta del archivo generado
    """
    # Crear carpeta output si no existe
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ips_publicas_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Escribir el CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["IP_Publica"])  # Header
        for ip in ips_publicas:
            writer.writerow([ip])
    
    return filepath


def mostrar_menu():
    """Muestra el menú principal del programa."""
    print("\n" + "="*50)
    print("     FILTRADOR DE IPs PÚBLICAS")
    print("="*50)
    print("\nSeleccione el método de entrada:")
    print("  1. 📝 Ingresar IPs manualmente")
    print("  2. 📋 Usar lista predefinida")
    print("  3. 📁 Cargar desde archivo CSV")
    print("  4. ❌ Salir")
    print("-"*50)


def main():
    """Función principal del programa."""
    print("\n🚀 Iniciando programa de filtrado de IPs...")
    
    while True:
        mostrar_menu()
        
        opcion = input("\nOpción [1-4]: ").strip()
        
        if opcion == '4':
            print("\n👋 ¡Hasta luego!")
            break
        
        # Obtener IPs según la opción seleccionada
        ips = set()
        
        if opcion == '1':
            ips = leer_ips_manual()
        elif opcion == '2':
            ips = leer_ips_lista()
        elif opcion == '3':
            ips = leer_ips_csv()
        else:
            print("\n⚠ Opción inválida. Por favor seleccione 1-4")
            continue
        
        if not ips:
            print("\n⚠ No se encontraron IPs para procesar")
            continue
        
        # Filtrar IPs públicas
        ips_publicas = filtrar_ips_publicas(ips)
        
        # Mostrar resumen
        print("\n" + "="*50)
        print(f"📊 RESUMEN:")
        print(f"  • IPs totales analizadas: {len(ips)}")
        print(f"  • IPs públicas encontradas: {len(ips_publicas)}")
        print(f"  • IPs privadas/reservadas filtradas: {len(ips) - len(ips_publicas)}")
        
        if ips_publicas:
            # Guardar resultado
            archivo_salida = guardar_resultado_csv(ips_publicas)
            print(f"\n✅ Resultado guardado en: {archivo_salida}")
            
            # Mostrar las IPs públicas encontradas
            print(f"\n🌐 IPs públicas encontradas:")
            for ip in ips_publicas:
                print(f"   • {ip}")
        else:
            print("\n⚠ No se encontraron IPs públicas en la entrada proporcionada")
        
        input("\n[Presione Enter para continuar...]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")