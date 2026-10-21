# One line per explicitly installed package: name, repo|foreign, size, install date, description
foreign=$(pacman -Qqm)
LC_ALL=C pacman -Qie | awk -v F="$foreign" '
BEGIN{n=split(F,a,"\n"); for(i=1;i<=n;i++) f[a[i]]=1}
/^Name/{name=$3} /^Description/{sub(/^Description *: /,""); d=$0} /^Installed Size/{sz=$4" "$5} /^Install Date/{sub(/^Install Date *: /,""); dt=$0}
/^$/{if(name){print name"\t"(name in f?"foreign":"repo")"\t"sz"\t"dt"\t"d}; name=""}'
