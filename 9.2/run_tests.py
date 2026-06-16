"""
Запуск тестов pytest-bdd из IDLE.
"""
import subprocess
import sys


def run_bdd_tests():
    """Запускает BDD тесты через pytest."""
    print("=" * 70)
    print("ЗАПУСК BDD ТЕСТОВ (pytest-bdd)")
    print("=" * 70)
    
    # Запускаем pytest
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'steps/', '-v'],
        capture_output=True,
        text=True
    )
    
    # Выводим результаты
    print(result.stdout)
    
    if result.stderr:
        print("ОШИБКИ:")
        print(result.stderr)
    
    print("=" * 70)
    
    return result.returncode == 0


if __name__ == "__main__":
    success = run_bdd_tests()
    if success:
        print("✅ ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
    else:
        print("❌ ТЕСТЫ УПАЛИ!")
    
    input("\nНажмите Enter для выхода...")
