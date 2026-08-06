"""
Системные уведомления для Windows (и других ОС).
"""
import os
import sys
import platform
import subprocess


def send_notification(title: str, message: str, timeout: int = 5):
    """
    Отправить системное уведомление.
    Поддерживает Windows (через PowerShell) и Linux/macOS (через notify-send).
    """
    system = platform.system()

    if system == "Windows":
        try:
            title_escaped = title.replace('"', '\\"')
            message_escaped = message.replace('"', '\\"')

            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -id $pid).Path)
            $notification.BalloonTipTitle = "{title_escaped}"
            $notification.BalloonTipText = "{message_escaped}"
            $notification.Visible = $true
            $notification.ShowBalloonTip({timeout * 1000})
            Start-Sleep -Seconds {timeout}
            $notification.Dispose()
            '''
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                shell=True,
                timeout=timeout + 2
            )
            return
        except Exception as e:
            print(f"Не удалось отправить уведомление через PowerShell: {e}")
            try:
                subprocess.run(
                    ["msg", "*", f"{title}: {message}"],
                    capture_output=True,
                    timeout=2
                )
            except:
                pass
        return

    elif system in ("Linux", "Darwin"):
        try:
            subprocess.run(
                ["notify-send", title, message, "-t", str(timeout * 1000)],
                capture_output=True,
                timeout=2
            )
        except Exception as e:
            print(f"Не удалось отправить уведомление через notify-send: {e}")