from leo_handover.cli import main

if __name__ == "__main__":
    import sys
    sys.argv.insert(1, "train")
    main()
