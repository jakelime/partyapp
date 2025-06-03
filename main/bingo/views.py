# main/bingo/views.py
import logging

from django.views.generic.base import TemplateView

from main.custom_mixin import LoginRequiredMixinNopassword
from .models import BingoBoard
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from .models import BingoBoard, winningNumber
import random

lg = logging.getLogger("django")


class HomeView(LoginRequiredMixinNopassword, TemplateView):
    template_name = "home_template.html"


class TestView(TemplateView):
    template_name = "bingo/testpage.html"

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if('draw' in request.POST):
            existing_winning_numbers = winningNumber.objects.values_list('num', flat=True)
            new_winning_number = random.randint(1, 120)  # Assuming Bingo numbers are 1-75

            # Keep generating until we find a number that's not already a winner
            while new_winning_number in existing_winning_numbers:
                new_winning_number = random.randint(1, 120)

            new_winning_number_obj = winningNumber(num=new_winning_number)
            new_winning_number_obj.save()

            # Get the list of all current winning numbers
            current_winning_numbers = list(winningNumber.objects.values_list('num', flat=True))

            # Query all existing Bingo boards
            all_boards = BingoBoard.objects.all()

            # Iterate through each board and call validate_board
            for board in all_boards:
                validated_board = board.validate_board(winning_numbers=current_winning_numbers)
                validated_board.save() # Save the updated is_winner status

            winning_boards = BingoBoard.objects.all().filter(is_winner=True)
            print(winning_boards)


            

        if('newboard' in request.POST):
            for i in range(0,300):
                obj = BingoBoard()
                obj.generateBoard()
                obj.save()

        if('reset' in request.POST):
            print("reset")
            winningNumber.objects.all().delete()   
            BingoBoard.objects.all().delete()

        return redirect(reverse("bingo:test"))


class PlayerView(TemplateView):
    template_name = "bingo/playerview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = BingoBoard.objects.get(pk=self.kwargs.get("pk"))
        context['board'] = board
        context['winning_numbers'] = list(winningNumber.objects.values_list('num', flat=True))

        return context

