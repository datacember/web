import sys
import os
import shutil

def is_kept(name: str) -> bool:
    """ defines a method to check if the format is done
        supposed to be lightweight method to check that the code is running legit and can render latest version of tempalte


        Things to do
        - there exist no XXX_files folders in templates
        - there exists no .html files in templates
        - check the images folder
    """


    folder_bin = 1 if f"{name}_files" in os.listdir("quarto") else 0
    file_bin = 1 if f"{name}.html" in os.listdir("quarto") else 0


    static = [img for img in os.listdir("static/images")]
    images = [img for img in os.listdir("quarto/images")]
    
    # TODO fix this
    if static != images:
        # checks that the images folder is in the right place
        return False

    if folder_bin + file_bin > 0:
        # checks that folders and files are in not in the wrong spot
        return False

    return True


def upkeep(name) -> None:
    """Tasks:
        - move .html
        - move files
        - rename .html
        - move images
    """
    def clean(name):
        try:
            print(f'wnat to remove {os.path.join(name, "quarto")}')
            os.remove(os.path.join("templates", f"{name}.html"))
        except Exception as E:
            print(str(E))

        try:
            print(f"want to remove static/{name}_files")
            shutil.rmtree(f"static/{name}_files")
        except Exception as E:
            print(str(E))

        try:
            shutil.rmtree("static/images")
        except Exception as E:
            print(str(E))

    def move(name):
        # process an individual name
        # rename all name.html links
        # for html file in file rename
        # rename then move

        with open(f'quarto/{name}.html', 'r', encoding='utf-8') as html:
            content = html.read()

        content = content.replace('images/', '/static/images/')
        content = content.replace(f'{name}_files/', f'/static/{name}_files/')

        with open(f'quarto/{name}.html', 'w', encoding='utf-8') as html:
            html.write(content)

        # move html to templates
        file = f'{name}.html'
        folder = f'{name}_files'

        shutil.move('quarto/'+file, 'templates/'+file)
        shutil.move('quarto/'+folder, 'static/'+folder)
        shutil.copytree('quarto/images', 'static/images')

    print(clean(name))
    print("moving")
    move(name)

    pass


if __name__ == '__main__':
    if "-u" in sys.argv:
        if is_kept():
            upkeep()

    if "-t" in sys.argv:
        print(is_kept())
