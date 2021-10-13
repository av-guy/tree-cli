from src.tree import Main, CLI

if __name__ == "__main__":
    cli = CLI()
    Main(cli.input_path, ascii=cli.ascii, files=cli.files)
