for file in _drafts/*.md; do
  awk '
  BEGIN { RS="\n"; FS="\n"; ORS="\n"; print_it=1; buffer=""; }
  $0 ~ /^description:/ { print_it=0; }
  $0 ~ /^pubDate:/ { print_it=1; gsub(/\n[ ]*/," ", buffer); gsub(/[ ]{2,}/, " ", buffer); printf "%s\n", buffer; buffer=""; }
  !print_it { buffer=sprintf("%s%s\n", buffer, $0); next; }
  print_it { print $0; }
  ' "$file" > tmp && mv tmp "$file"
done