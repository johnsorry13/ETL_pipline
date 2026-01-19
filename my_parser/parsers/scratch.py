from pathlib import Path
import pandas
import pandas as pd

urls_path = (Path(__file__).parent.parent
               / "sources" / "URLs.xlsx")

print(urls_path)
# df = pd.read_excel(urls_path)
# print(df)