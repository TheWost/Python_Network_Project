
class Utils:
    @staticmethod
    def loading_anim(stop_event,text):
        """FUNCTION USED WITHIN A THREAD"""
        animation = ["|", "/", "-", "\\"]
        idx = 0
        
        def anim(i):
            return animation[i % len(animation)]

        while not stop_event.is_set():
            print(f"\r{text}... [{anim(idx) * 3}]", end ="", flush=True)
            time.sleep(0.1)
            idx += 1


