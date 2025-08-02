import sys
import os

def chunk_atoms(atoms, chunk_size):
    for i in range(0, len(atoms), chunk_size):
        yield atoms[i:i + chunk_size]

def format_coord(coord):
    """
    格式化坐标：
    - 保留6位小数
    - 如果末尾是两个0，则去掉这两个0
    """
    f = float(coord)
    s = f"{f:.6f}"
    if s.endswith("00") and not s.endswith("0000"):
        s = s[:-2]
    return s

def generate_latex_table(atoms, name):
    lines = []

    if len(atoms) <= 34:
        # 单栏表格
        lines.append("\\begin{table}[H]")
        lines.append("\\centering")
        lines.append(f"\\caption{{Optimized geometry of \\textbf{{{name}}} in the S$_0$ state.}}")
        lines.append("\\begin{tabular}{lrrr}")
        lines.append("\\hline")
        lines.append("Atoms & X (\\AA) & Y (\\AA) & Z (\\AA) \\\\")
        lines.append("\\hline")
        for atom in atoms:
            coords = [format_coord(c) for c in atom[1:]]
            lines.append(f"{atom[0]} & {coords[0]} & {coords[1]} & {coords[2]} \\\\")
        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append("\\end{table}")
        return "\n".join(lines)

    # 多栏分页表格（适用于原子数 > 34）
    atoms_per_page = 66
    atoms_per_column = 33

    chunks = list(chunk_atoms(atoms, atoms_per_page))

    for page_index, chunk in enumerate(chunks):
        if page_index > 0:
            lines.append("\\clearpage")
        lines.append("\\centering")
        lines.append("\\begin{longtable}{cccccccc}")
        lines.append(f"\\caption{{Optimized geometry of \\textbf{{{name}}} in the S\\$_0$ state.}} \\\\")
        lines.append("\\toprule")
        lines.append("Atoms & X (\\AA) & Y (\\AA) & Z (\\AA) & Atoms & X (\\AA) & Y (\\AA) & Z (\\AA) \\\\")
        lines.append("\\midrule")
        lines.append("\\endfirsthead")
        lines.append("\\toprule")
        lines.append("Atoms & X (\\AA) & Y (\\AA) & Z (\\AA) & Atoms & X (\\AA) & Y (\\AA) & Z (\\AA) \\\\")
        lines.append("\\midrule")
        lines.append("\\endhead")
        lines.append("\\bottomrule")
        lines.append("\\endfoot")

        left = chunk[:atoms_per_column]
        right = chunk[atoms_per_column:]

        # 填充右栏为空元组
        if len(right) < len(left):
            right.extend([("", "", "", "")] * (len(left) - len(right)))

        for l, r in zip(left, right):
            l_coords = [format_coord(c) for c in l[1:]]
            if r[0]:
                r_coords = [format_coord(c) for c in r[1:]]
                line = f"{l[0]} & {l_coords[0]} & {l_coords[1]} & {l_coords[2]} & {r[0]} & {r_coords[0]} & {r_coords[1]} & {r_coords[2]} \\\\"
            else:
                line = f"{l[0]} & {l_coords[0]} & {l_coords[1]} & {l_coords[2]} & & & & \\\\"
            lines.append(line)

        lines.append("\\end{longtable}")

    return "\n".join(lines)

def read_xyz(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()[2:]  # 跳过前两行
    atoms = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 4:
            atoms.append((parts[0], parts[1], parts[2], parts[3]))
    return atoms

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python3 xyz_to_latex.py input.xyz")
        sys.exit(1)

    xyz_file = sys.argv[1]
    molecule_name = os.path.splitext(os.path.basename(xyz_file))[0]
    atoms = read_xyz(xyz_file)

    print(f"原子数: {len(atoms)}\n")
    latex_code = generate_latex_table(atoms, molecule_name)
    print(latex_code)

