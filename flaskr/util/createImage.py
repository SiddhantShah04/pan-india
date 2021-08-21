from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen


def drawImage(formData):
    widthOfTemplate = int(formData["widthOfTemplate"])
    heightOfTemplate = int(formData["heightOfTemplate"])
    imageUrl = formData['imageUrl']
    im = Image.open(urlopen(imageUrl))
    # print(formData)
    genrateImage = im.resize(
        (widthOfTemplate, heightOfTemplate), Image.ANTIALIAS)
    imageWriter = ImageDraw.Draw(genrateImage)
    for elt in formData['dynamicFields']:

        positionX = int(elt['position']['x'])
        positionY = int(elt['position']['y'])

        if(elt['fieldType'] == 'text'):
            fontName = elt['fontStyle']  # known section

            font = ImageFont.truetype(
                f"fonts/{fontName}", int(elt["fontSize"]))

            imageWriter.text(
                (positionX, positionY), elt['value'], fill=elt['fontColor'], font=font)
        elif(elt['fieldType'] == 'image'):
            # add the image to specific position
            imageUrl = elt["value"]
            imageUrl = Image.open(urlopen(imageUrl))
            offset = (positionX, positionY)

            genrateImage.paste(imageUrl, offset)
    return(genrateImage)
