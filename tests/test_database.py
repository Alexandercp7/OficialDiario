import unittest
import database

class TestDatabaseModule(unittest.TestCase):
    def test_hash_and_verify_password(self):
        """Verifica el hasheo criptográfico y la verificación segura de contraseñas."""
        password = "MiPasswordSeguro123!"
        pwd_hash, salt = database.hash_password(password)

        self.assertIsNotNone(pwd_hash)
        self.assertIsNotNone(salt)
        self.assertGreater(len(pwd_hash), 20)
        self.assertGreater(len(salt), 10)

        # Debe verificar correctamente
        self.assertTrue(database.verify_password(password, salt, pwd_hash))

        # Debe rechazar contraseña incorrecta
        self.assertFalse(database.verify_password("PasswordErroneo", salt, pwd_hash))

    def test_generate_link_code(self):
        """Verifica la generación de códigos de vinculación de 6 caracteres."""
        code1 = database.generate_link_code()
        code2 = database.generate_link_code()

        self.assertEqual(len(code1), 6)
        self.assertEqual(len(code2), 6)
        self.assertTrue(code1.isalnum())
        self.assertTrue(code1.isupper())

    def test_user_lifecycle_and_criteria(self):
        """Verifica creación de usuario, login, criterios con juzgados y sesión."""
        unique_email = f"test_juridico_{database.generate_link_code().lower()}@lexmonitortest.com"
        name = "Lic. Evaluación Unitaria"
        password = "PasswordPrueba2026!"

        # 1. Crear usuario
        user_dict, err = database.create_user(name, unique_email, password)
        self.assertIsNone(err, f"Error creando usuario: {err}")
        self.assertIsNotNone(user_dict)
        user_id = user_dict["id"]
        self.assertEqual(user_dict["email"], unique_email)

        # 2. Intentar duplicar email debe fallar
        _, dup_err = database.create_user("Otro Nombre", unique_email, "OtraPassword")
        self.assertIsNotNone(dup_err)
        self.assertIn("registrad", dup_err.lower())

        # 3. Autenticación válida e inválida
        auth_user, auth_err = database.authenticate_user(unique_email, password)
        self.assertIsNone(auth_err)
        self.assertEqual(auth_user["id"], user_id)

        _, bad_err = database.authenticate_user(unique_email, "PasswordInvalida")
        self.assertIsNotNone(bad_err)

        # 4. Manejo de tokens de sesión
        token = database.create_session_token(user_id)
        self.assertIsNotNone(token)
        fetched_user = database.get_user_by_token(token)
        self.assertIsNotNone(fetched_user)
        self.assertEqual(fetched_user["id"], user_id)

        # 5. Agregar y listar criterios con juzgado específico
        criterio, c_err = database.add_user_criterion(
            user_id=user_id,
            tipo="Expediente",
            valor="888/2026",
            juzgado="Juzgado Segundo Mercantil"
        )
        self.assertIsNone(c_err)
        self.assertEqual(criterio["valor"], "888/2026")
        self.assertEqual(criterio["juzgado"], "Juzgado Segundo Mercantil")

        criteria_list = database.get_user_criteria(user_id)
        self.assertTrue(any(c["valor"] == "888/2026" for c in criteria_list))

        # 6. Actualizar configuración de notificaciones
        ok_cfg = database.update_user_notification_config(user_id, {
            "channel": "email",
            "email": {"recipient_email": "notificaciones@lexmonitortest.com"}
        })
        self.assertTrue(ok_cfg)
        cfg = database.get_user_notification_config(user_id)
        self.assertEqual(cfg.get("channel"), "email")
        self.assertEqual(cfg.get("email", {}).get("recipient_email"), "notificaciones@lexmonitortest.com")

        # 7. Eliminar criterio
        del_ok = database.delete_user_criterion(user_id, valor="888/2026")
        self.assertTrue(del_ok)
        criteria_post = database.get_user_criteria(user_id)
        self.assertFalse(any(c["valor"] == "888/2026" for c in criteria_post))

        # 8. Limpiar sesión
        database.delete_session_token(token)
        self.assertIsNone(database.get_user_by_token(token))

    def test_timezone_utilities(self):
        """Verifica que las funciones de hora Mérida retornen cadenas y datetimes válidos."""
        now_m = database.ahora_merida()
        self.assertIsNotNone(now_m)
        self.assertEqual(now_m.tzinfo.utcoffset(now_m).total_seconds(), -6 * 3600)

        today_str = database.fecha_hoy_merida()
        self.assertRegex(today_str, r"^\d{4}-\d{2}-\d{2}$")

        time_str = database.format_merida_time(now_m)
        self.assertRegex(time_str, r"^\d{2}:\d{2}:\d{2}$")

if __name__ == "__main__":
    unittest.main()
