# Grizzly Manager - Cura plugin
![Grizzly Manager](https://github.com/big-vl/GrizzlyManager/raw/master/GrizzlyManager.png)
## Что есть в плагине?:
- Калибровочный кубик XYZ
> С его помощью очень удобно набирать размерность, настраивая шаги по миллиметрам, тестировать качество экструзии, температуру и уровень вибрации.
- Калибровочная башня температуры 230-260 градусов
> Как несложно догадаться, её используют для регулировки нагрева, часто применяется такая температура для PETG, ABS.
> Печатая башню разными видами термопластика, можно определить, при какой температуре качество печати будет наилучшим. 
- Input Shaping калибровка (для Marlin)
> Это может сохранить износ компонентов принтера и увеличить срок их службы. 
> Без Input Shaping также существует повышенный риск откручивания или ослабления некоторых деталей, за счет повышенной вибрации. 

## Стабильная версия:
[Скачать GrizzlyManager](https://github.com/big-vl/GrizzlyManager/releases/tag/release)
## Установка
Как установить плагин:
### Linux:
- находится в папке `~/.local/share/cura/5.2/plugins`
- Скачайте плагин и разархивируйте его.
- Переместите всю папку в папку плагинов.
- Перезагрузите Cura

### Windows:
- находится в папке «программные файлы».
- На компьютере перейдите в папку Cura.
- Переместите всю папку в папку плагинов.
- Перезагрузите Cura

### Mac:
- находится в папке приложений
- Откройте папку и найдите следующий путь к файлу: Cura/Contents/Resources/cura/plugins
- Эта папка содержит несколько других плагинов, таких как «3MF Reader» и «Autosave».
- Скачайте плагин и разархивируйте его.
- Переместите всю папку в папку плагинов.
- Перезагрузите Cura

## Как калибровать Input shaping на Marlin?
1. Добавляем модель на стол:
![Добавляем модель](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step1_add_ringing_tower.png)
2. Добавляем пост-обработку модели
![Добавляем пост-обработку](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step2_add_gcode.png)
3. Жмем Добавить скрипт, выбираем в первом этапе `Input Shaping While`:
    > Устанавливаем параметры слоя переключения `Step height` с учетом того где у нас будет заканчиваться секция на калибровочной модели. Обычно высоту слоя ставят 0.2 и 25 слоев (см. правую часть скриншота) 
    > Устанавливаем ускорение при котором хотим печатать, для Flying Bear Ghost 6 это лимит в 3000.
    > Устанавливаем начальную частоту `Start Freq`, я поставил 0, потому что я еще не знаю частоту которая мне нужна.
    > Устанавливаем `Step delta freq` - этот параметр отвечает сколько мы будем прибавлять к каждой секции калибровочной модели.
    > Устанавливаем `Freq at` для X или Y или `All` (к всем) - я оставил `All` потому что я не знаю какая частота подходит к X или Y
    > Устанавливаем `Set damping ration (Zeta)` - я оставил 0.0, значение меняться не будет, потому что я еще не знаю сколько мне ставить.
![Добавляем пост-обработку](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step3_add_script.png)
### Печатаем и калибруем:
4. Вот у нас появилась калибровочная модель, нам не нужен штангенциркуль.
![Секция 1 для калибровки](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step4_one_section.jpg)
Здесь выбираем ту секцию которая самая лучшая, т.е. максимально не имеет эхо, считаем снизу и видим что это снизу 4тая секция, при установке добавления параметра `Start Freq` - 0 и `Step delta freq` - 5 то это 35Hz на оси Y, переварачиваем на X и смотрим что писать в X.
5. Идем в принтер и вводим параметры `X frequency` и `Y frequency`
![Секция 1 для калибровки](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step5_insert_settings.jpg)
**ВНИМАНИЕ НА КАЖДЫЙ ПРИНТЕР И НАТЯЖКУ РЕМНЕЙ СВОИ ПАРАМЕТРЫ!** \
**Вы спросите почему у меня на моделе одни параметры, а в принтере другие поставил?**
Потому что я перетягивал ремни по новой.
6. Теперь как мы определились с частотой идем далее, добавляем второй скрипт и изменяем первый, например правильное значение вы выбрали 35 то указываем его в скрипте `Input Shaping While` с параметром чуть ниже и шагом 1 для калибровки. В скрипте `Input Shaping Zeta` указываем опять слои для секции `Step height`, в параметр `Set Shaping Zeta Testing at step` указываем значение для Zeta\Damping ratio с каким шагом будет происходить изменение этого параметра. Отправляем на печать.
![Изменяем параметры Input Shaping While](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step6_change_settings.png)
![Изменяем параметры Input Shaping While](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step6_add_zeta.png)
7. Смотрим вторую часть модели. Например у вас в `Input Shaping Zeta` стоит шаг в 0.5 то правильная секция в моделе будет 4тая с параметром 0.2 для параметра `* damping` (* - для X или Y)  
![Изменяем параметры Input Shaping While](https://github.com/big-vl/GrizzlyManager/raw/dev/images/step7_select_zeta.jpg)
8. Все готово, вы откалибровали `Input Shaping для Marlin`, не забудьте удалить пост-скрипты - они больше нам не нужны будут, до момента перетяжки ремней или их раслабления (ухудшения качества печати).

> PS: При добавлении модели плагин выключает такие параметры как `Linear Advance` и `Использовать адаптивные слои`, включает `Режим вазы (Спирально печатать внешний контур)`, от себя порекомендую установить параметры `Слои дна` - 0 и `Слои крышки` - 0, скорость пачати для Flying Bear 6 я установил в 150мм\с, ах да еще чуть не забыл `Минимальное время слоя` - 3 секунды.
![Воздействие Grizzly Manager на профиль](https://github.com/big-vl/GrizzlyManager/raw/dev/images/spiral_true_and_adaptive_false.png)
![Воздействие Grizzly Manager на профиль](https://github.com/big-vl/GrizzlyManager/raw/dev/images/linear_advance.png)
![Воздействие Grizzly Manager на профиль](https://github.com/big-vl/GrizzlyManager/raw/dev/images/min_time_3.png)
## Как калибровать в Prusa Slicer на Marline:

Input Shaping частота:
```
; Input Shaping Frequency Testing
{if layer_z==layer_height}M204 P1500; Set Acceleration at Layer 1{endif}
{if layer_z==5}M204 P2000; Set Acceleration at Layer 5{endif}
{if layer_z==10}M204 P2500; Set Acceleration at Layer 10{endif}
{if layer_z==15}M204 P3000; Set Acceleration at Layer 15{endif}
{if layer_z==20}M204 P3500; Set Acceleration at Layer 20{endif}
{if layer_z==25}M204 P4000; Set Acceleration at Layer 25{endif}
{if layer_z==30}M204 P4500; Set Acceleration at Layer 30{endif}
{if layer_z==35}M204 P5000; Set Acceleration at Layer 35{endif}
{if layer_z==40}M204 P5500; Set Acceleration at Layer 40{endif}
{if layer_z==45}M204 P6000; Set Acceleration at Layer 45{endif}
{if layer_z==50}M204 P6500; Set Acceleration at Layer 50{endif}
{if layer_z==55}M204 P7000; Set Acceleration at Layer 55{endif}
```

Input Shaping Zeta:
```
; Input Shaping Zeta Testing
{if layer_z==layer_height}M593 D0.1; Set Input Shaping Zeta at Layer 1{endif}
{if layer_z==5}M593 D0.15; Set Input Shaping Zeta at Layer 5{endif}
{if layer_z==10}M593 D0.2; Set Input Shaping Zeta at Layer 10{endif}
{if layer_z==15}M593 D0.25; Set Input Shaping Zeta at Layer 15{endif}
{if layer_z==20}M593 D0.3; Set Input Shaping Zeta at Layer 20{endif}
{if layer_z==25}M593 D0.35; Set Input Shaping Zeta at Layer 25{endif}
{if layer_z==30}M593 D0.4; Set Input Shaping Zeta at Layer 30{endif}
{if layer_z==35}M593 D0.5; Set Input Shaping Zeta at Layer 35{endif}
{if layer_z==40}M593 D0.6; Set Input Shaping Zeta at Layer 40{endif}
{if layer_z==45}M593 D0.7; Set Input Shaping Zeta at Layer 45{endif}
{if layer_z==50}M593 D0.8; Set Input Shaping Zeta at Layer 50{endif}
{if layer_z==55}M593 D0.9; Set Input Shaping Zeta at Layer 55{endif}
```

Вставьте приведенный выше блок кода в `«Настройки принтера» -> «Пользовательский G-код» -> «G-код перед изменением слоя»`; `"Printer Settings" -> "Custom G-code" -> "Before layer change G-code"` под любым существующим кодом, который у вас может быть.
Код выполняет изменение с учетом слоя, если слой layer_z равно 5, то устанавливает значение для zeta M593 D0.15;
### Бонусы:
[![Подставка для кубика](https://img.youtube.com/vi/rGCNgz-JkqQ/maxresdefault.jpg)](https://www.youtube.com/embed/rGCNgz-JkqQ)
