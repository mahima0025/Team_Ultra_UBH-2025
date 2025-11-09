for c in /dev/gpiochip*; do
  echo "== $c =="; gpioinfo "$c" | egrep 'line +2:|line +3:'
done

