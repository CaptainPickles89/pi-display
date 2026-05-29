from PIL import Image, ImageDraw, ImageFont
import datetime
from inky.auto import auto


def get_date():

    # Prepare the display
    inky = auto()
    with Image.open("./resources/imgs/Date-bg1-01.png") as img:
        img = img.resize(inky.resolution)
        draw = ImageDraw.Draw(img)
        display_width, display_height = (
            img.size
        )  # Assuming image is already resized to fit display

        # Pull the date elements into seperate variables
        todays_date = datetime.datetime.now()
        date_num = todays_date.strftime("%d")
        date_day = todays_date.strftime("%A")
        date_month = todays_date.strftime("%B")

        # Font settings (update path to your font file)
        font_path = "./resources/fonts/Roboto-Medium.ttf"
        num_font = ImageFont.truetype(font_path, 90)
        text_font = ImageFont.truetype(font_path, 50)

        # Define Displayed Lines
        line1 = f"{date_day}"
        line2 = f"{date_num}"
        line3 = f"{date_month}"

        # Measure the width and height of each line
        text_spacing = 15  # Spacing between lines

        # Draw first line (centered horizontally)
        b1 = draw.textbbox((0, 0), line1, font=text_font)
        x_position = (display_width - (b1[2] - b1[0])) // 2
        y_position = 90
        draw.text((x_position, y_position), line1, font=text_font, fill="black")

        # Draw second line with larger font (centered horizontally)
        b2 = draw.textbbox((0, 0), line2, font=num_font)
        x_position = (display_width - (b2[2] - b2[0])) // 2
        y_position += (b1[3] - b1[1]) + text_spacing
        draw.text((x_position, y_position), line2, font=num_font, fill="black")

        # Draw third line (centered horizontally)
        b3 = draw.textbbox((0, 0), line3, font=text_font)
        x_position = (display_width - (b3[2] - b3[0])) // 2
        y_position += (b2[3] - b2[1]) + text_spacing
        draw.text((x_position, y_position), line3, font=text_font, fill="black")

        inky.set_image(img)
        inky.show()


if __name__ == "__main__":
    get_date()
