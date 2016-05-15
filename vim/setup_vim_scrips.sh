DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
if [ -e ~/.vim ]
then
  echo "removing old .vim"
  rm -r ~/.vim
fi

if [ -e ~/.vimrc ]
then
  echo "removing old .vimrc"
  rm ~/.vimrc
fi

echo setting up .vimrc and .vim script dirs
ln -s $DIR ~/.vim
ln -s $DIR/vimrc ~/.vimrc
