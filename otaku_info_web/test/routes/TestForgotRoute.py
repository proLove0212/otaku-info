"""LICENSE
Copyright 2020 Hermann Krumrey <hermann@krumreyh.com>

This file is part of otaku-info-web.

otaku-info-web is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

otaku-info-web is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with otaku-info-web.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

from unittest.mock import patch
from otaku_info_web.test.TestFramework import _TestFramework


class TestForgotRoute(_TestFramework):
    """
    Class that tests password reset features
    """

    def test_page_get(self):
        """
        Tests getting the page
        :return: None
        """
        resp = self.client.get("/forgot")
        self.assertTrue(b"<!--user_management/forgot.html-->" in resp.data)

    def test_resetting_password(self):
        """
        Tests successfully resetting a password
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            with patch("otaku_info_web.routes.user_management.send_email") as m:
                with patch("otaku_info_web.routes.user_management.generate_random",
                           lambda x: "testpass"):
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/forgot",
                        follow_redirects=True,
                        data={
                            "email": user.email,
                            "g-recaptcha-response": ""
                        }
                    )
                    self.assertEqual(1, m.call_count)

            self.assertTrue(b"Password was reset successfully" in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertFalse(user.verify_password(password))
            self.assertTrue(user.verify_password("testpass"))

    def test_unsuccessfully_resetting_password(self):
        """
        Tests unsuccessfully resetting a password
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            with patch("otaku_info_web.routes.user_management.send_email") as m:
                with patch("otaku_info_web.routes.user_management.generate_random",
                           lambda x: "testpass"):
                    self.assertEqual(0, m.call_count)
                    resp = self.client.post(
                        "/forgot",
                        follow_redirects=True,
                        data={
                            "email": user.email + "AAA",
                            "g-recaptcha-response": ""
                        }
                    )
                    self.assertEqual(0, m.call_count)

            self.assertTrue(b"Password was reset successfully" in resp.data)
            self.assertTrue(b"<!--static/index.html-->" in resp.data)
            self.assertTrue(user.verify_password(password))
            self.assertFalse(user.verify_password("testpass"))

    def test_invalid_recaptcha(self):
        """
        Tests that invalid ReCaptcha responses are handled correctly
        :return: None
        """
        user, password, _ = self.generate_sample_user()
        with self.client:
            with patch("otaku_info_web.routes.user_management.send_email") as m:
                with patch("otaku_info_web.routes.user_management.generate_random",
                           lambda x: "testpass"):
                    with patch("otaku_info_web.routes.user_management"
                               ".verify_recaptcha",
                               lambda x, y, z: False):
                        self.assertEqual(0, m.call_count)
                        resp = self.client.post(
                            "/forgot",
                            follow_redirects=True,
                            data={
                                "email": user.email,
                                "g-recaptcha-response": ""
                            }
                        )
                        self.assertEqual(0, m.call_count)

            self.assertTrue(b"Invalid ReCaptcha Response" in resp.data)
            self.assertTrue(b"<!--user_management/forgot.html-->" in resp.data)
            self.assertTrue(user.verify_password(password))
            self.assertFalse(user.verify_password("testpass"))
