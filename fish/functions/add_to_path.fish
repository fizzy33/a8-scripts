


function add_to_path --description "append to your PATH"
  set -l __pos last
  for path in $argv
    switch $path
      case --first
        set __pos first
      case --last
        set __pos last
      case '*'
        set -l resolved_path (realpath $path --quiet)
        if test -d $resolved_path
          if not contains $resolved_path $PATH
            if [ "$__pos" = "last" ]
              set --export PATH $PATH $resolved_path
            else
              set --export PATH $resolved_path $PATH
            end
          end
        end
      end
  end
end
