import flet as ft


def main(page: ft.Page):
    page.title = "Calc Reductor + VFD"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO

    def make_field(label: str, default: str = "", hint: str = ""):
        return ft.TextField(
            label=label,
            value=default,
            hint_text=hint,
            keyboard_type=ft.KeyboardType.NUMBER,
            text_align=ft.TextAlign.RIGHT,
            border_radius=8,
            dense=True,
        )

    tf_rpm_motor = make_field("RPM del Motor (a 60 Hz)", "1700")
    tf_f_nom = make_field("Frecuencia Nominal (Hz)", "60")
    tf_i_red = make_field("Relación del Reductor (i)", "20")
    tf_z_chica = make_field("Dientes Estrella Chica", "13")
    tf_z_grande = make_field("Dientes Estrella Grande", "", "Vacío para calcular")
    tf_rpm_salida = make_field("RPM de Salida deseada", "16")
    tf_f_vfd = make_field("Frecuencia Variador (Hz)", "37.35")

    todos_campos = [
        tf_rpm_motor,
        tf_f_nom,
        tf_i_red,
        tf_z_chica,
        tf_z_grande,
        tf_rpm_salida,
        tf_f_vfd,
    ]

    estado = ft.Text(
        "Deja EN BLANCO el único dato que quieres calcular y presiona Calcular.",
        size=13,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_700,
    )

    banner = ft.Container(
        content=estado,
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.BLUE_50,
    )

    def set_status(msg: str, text_color, bg_color):
        estado.value = msg
        estado.color = text_color
        banner.bgcolor = bg_color

    def parse_val(tf: ft.TextField):
        raw = (tf.value or "").strip().replace(",", ".")
        if raw == "":
            return None
        return float(raw)

    def reset_colors():
        for tf in todos_campos:
            tf.bgcolor = None

    def limpiar_todo(e):
        reset_colors()
        for tf in [tf_rpm_motor, tf_i_red, tf_z_chica, tf_z_grande, tf_rpm_salida, tf_f_vfd]:
            tf.value = ""
        set_status("Campos limpios. Llena 5 datos y deja 1 vacío.", ft.Colors.BLUE_700, ft.Colors.BLUE_50)
        page.update()

    def calcular(e):
        reset_colors()
        try:
            rpm_m = parse_val(tf_rpm_motor)
            f_nom = parse_val(tf_f_nom)
            i_red = parse_val(tf_i_red)
            z_c = parse_val(tf_z_chica)
            z_g = parse_val(tf_z_grande)
            rpm_s = parse_val(tf_rpm_salida)
            f_vfd = parse_val(tf_f_vfd)
        except ValueError:
            set_status(
                "Error: ingresa solo números válidos (usa punto decimal).",
                ft.Colors.RED_700,
                ft.Colors.RED_50,
            )
            page.update()
            return

        if f_nom is None or f_nom <= 0:
            set_status(
                "Error: la frecuencia nominal debe ser mayor a 0 (ej. 60).",
                ft.Colors.RED_700,
                ft.Colors.RED_50,
            )
            page.update()
            return

        incognitas = [
            ("RPM del Motor", rpm_m, tf_rpm_motor, 0),
            ("Relación del Reductor", i_red, tf_i_red, 2),
            ("Dientes Estrella Chica", z_c, tf_z_chica, 0),
            ("Dientes Estrella Grande", z_g, tf_z_grande, 0),
            ("RPM de Salida", rpm_s, tf_rpm_salida, 2),
            ("Frecuencia Variador (Hz)", f_vfd, tf_f_vfd, 2),
        ]

        vacios = [item for item in incognitas if item[1] is None]

        if len(vacios) != 1:
            msg = (
                "Todos los campos tienen valor. Borra el campo que deseas calcular."
                if len(vacios) == 0
                else f"Dejaste {len(vacios)} campos vacíos. Deja SOLO UNO vacío."
            )
            set_status(msg, ft.Colors.AMBER_900, ft.Colors.AMBER_50)
            page.update()
            return

        nombre, _, campo_obj, dec = vacios[0]

        try:
            if campo_obj is tf_rpm_salida:
                if i_red == 0 or z_g == 0:
                    raise ZeroDivisionError
                res = (rpm_m * (f_vfd / f_nom)) / (i_red * (z_g / z_c))
            elif campo_obj is tf_f_vfd:
                if i_red == 0 or z_g == 0 or rpm_m == 0:
                    raise ZeroDivisionError
                rpm_max_nom = rpm_m / (i_red * (z_g / z_c))
                res = f_nom * (rpm_s / rpm_max_nom)
            elif campo_obj is tf_z_grande:
                if rpm_s == 0 or i_red == 0 or f_vfd == 0:
                    raise ZeroDivisionError
                i_total_req = (rpm_m * (f_vfd / f_nom)) / rpm_s
                res = z_c * (i_total_req / i_red)
            elif campo_obj is tf_z_chica:
                if rpm_s == 0 or i_red == 0 or f_vfd == 0:
                    raise ZeroDivisionError
                i_total_req = (rpm_m * (f_vfd / f_nom)) / rpm_s
                res = z_g / (i_total_req / i_red)
            elif campo_obj is tf_i_red:
                if rpm_s == 0 or z_g == 0 or f_vfd == 0:
                    raise ZeroDivisionError
                i_total_req = (rpm_m * (f_vfd / f_nom)) / rpm_s
                res = i_total_req / (z_g / z_c)
            elif campo_obj is tf_rpm_motor:
                if z_c == 0 or f_vfd == 0:
                    raise ZeroDivisionError
                res = rpm_s * i_red * (z_g / z_c) * (f_nom / f_vfd)

            campo_obj.value = f"{res:.{dec}f}"
            campo_obj.bgcolor = ft.Colors.GREEN_50
            set_status(f"Calculado ({nombre}): {res:.{dec}f}", ft.Colors.GREEN_800, ft.Colors.GREEN_50)

        except ZeroDivisionError:
            set_status(
                "Error: división entre cero. Revisa que no haya ceros en divisores.",
                ft.Colors.RED_700,
                ft.Colors.RED_50,
            )

        page.update()

    page.add(
        ft.Text("Transmisión y Variador (VFD)", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Llena 5 valores y deja 1 en blanco para despejarlo.", size=12, color=ft.Colors.GREY_700),
        ft.Divider(height=10),
        tf_rpm_motor,
        tf_f_nom,
        tf_i_red,
        tf_z_chica,
        tf_z_grande,
        tf_rpm_salida,
        tf_f_vfd,
        ft.Row(
            [
                ft.Button("Calcular", on_click=calcular, expand=True),
                ft.Button("Limpiar", on_click=limpiar_todo),
            ],
            spacing=10,
        ),
        banner,
    )


ft.run(main)