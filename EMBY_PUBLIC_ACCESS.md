# Настройка публичного доступа к Emby серверу

## Проблема

Ваш Emby сервер находится по адресу `http://192.168.1.60:8096`, который является локальным IP в вашей домашней сети. Replit работает в облаке и не может подключиться к локальным адресам.

## Решения

### Вариант 1: Cloudflare Tunnel (Рекомендуется)

**Преимущества:** Бесплатно, безопасно, не требует проброса портов

1. Зарегистрируйтесь на [Cloudflare](https://www.cloudflare.com/)
2. Установите `cloudflared` на компьютер с Emby:
   ```bash
   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   
   # Windows - скачайте с https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

3. Авторизуйтесь:
   ```bash
   cloudflared tunnel login
   ```

4. Создайте туннель:
   ```bash
   cloudflared tunnel create emby-tunnel
   ```

5. Настройте конфигурацию (`~/.cloudflared/config.yml`):
   ```yaml
   tunnel: <TUNNEL-ID>
   credentials-file: /home/user/.cloudflared/<TUNNEL-ID>.json
   
   ingress:
     - hostname: emby.yourdomain.com
       service: http://localhost:8096
     - service: http_status:404
   ```

6. Запустите туннель:
   ```bash
   cloudflared tunnel run emby-tunnel
   ```

7. Обновите `EMBY_SERVER_URL` в Replit Secrets на `https://emby.yourdomain.com`

### Вариант 2: ngrok (Быстрое тестирование)

**Преимущества:** Очень быстрая настройка
**Недостатки:** URL меняется при перезапуске (платная версия имеет постоянный URL)

1. Зарегистрируйтесь на [ngrok.com](https://ngrok.com/)
2. Установите ngrok:
   ```bash
   # Linux/Mac
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   tar xvzf ngrok-v3-stable-linux-amd64.tgz
   sudo mv ngrok /usr/local/bin/
   
   # Windows - скачайте с ngrok.com
   ```

3. Авторизуйтесь:
   ```bash
   ngrok config add-authtoken <YOUR-TOKEN>
   ```

4. Запустите туннель:
   ```bash
   ngrok http 8096
   ```

5. Скопируйте публичный URL (например: `https://abc123.ngrok.io`)
6. Обновите `EMBY_SERVER_URL` в Replit Secrets

### Вариант 3: Проброс портов на роутере + DynDNS

**Преимущества:** Полный контроль
**Недостатки:** Требует настройки роутера, менее безопасно

1. Настройте проброс портов на роутере:
   - Внешний порт: 8096
   - Внутренний IP: 192.168.1.60
   - Внутренний порт: 8096
   - Протокол: TCP

2. Зарегистрируйтесь на DynDNS сервисе (No-IP, DuckDNS, и т.д.)
3. Настройте динамический DNS для вашего IP
4. Обновите `EMBY_SERVER_URL` на `http://yourdomain.ddns.net:8096`

**⚠️ Важно:** При использовании проброса портов настройте HTTPS и сильный пароль для Emby!

## Проверка подключения

После настройки:

1. Откройте логи бота в Replit
2. Перезапустите workflow "Telegram Bot"
3. Проверьте логи на наличие:
   - ✅ `Успешное подключение к Emby серверу!` - всё работает
   - ❌ `Не удалось подключиться к Emby серверу` - проверьте настройки

## Тестирование бота

1. Найдите вашего бота в Telegram (имя указано при создании в @BotFather)
2. Напишите `/start`
3. Вы должны увидеть главное меню с кнопками
4. Нажмите "⚙️ Настройки" чтобы проверить статус подключения к Emby

## Безопасность

- Используйте HTTPS для публичного доступа к Emby
- Настройте сильные пароли
- Ограничьте доступ к API ключу Emby
- Регулярно обновляйте Emby Server
- Используйте firewall для ограничения доступа
