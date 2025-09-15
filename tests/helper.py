def create_morph_data_file(
    data_dir_path, x_morph, y_morph, x_target, y_target
):
    morph_file = data_dir_path / "morph_data"
    morph_data_text = [
        str(x_morph[i]) + " " + str(y_morph[i]) for i in range(len(x_morph))
    ]
    morph_data_text = "\n".join(morph_data_text)
    morph_file.write_text(morph_data_text)
    target_file = data_dir_path / "target_data"
    target_data_text = [
        str(x_target[i]) + " " + str(y_target[i]) for i in range(len(x_target))
    ]
    target_data_text = "\n".join(target_data_text)
    target_file.write_text(target_data_text)
    return morph_file, target_file
